<template>
  <div class="container">
    <!-- 头部 -->
    <header class="header">
      <h1>{{ t('需求生成测试用例系统') }}</h1>
      <div class="header-actions">
        <el-button
          @click="showUserGuide"
          size="small"
          type="info"
          circle
          :title="t('使用说明')"
        >
          📖
        </el-button>
        <el-button
          @click="handleLanguageToggle"
          size="small"
          type="primary"
          circle
          :title="languageStore.currentLanguage === 'zh' ? t('Switch to English') : t('切换到中文')"
        >
          {{ languageStore.currentLanguage === 'zh' ? 'EN' : '中' }}
        </el-button>
        <div class="header-info">
          <div class="model-info" v-if="modelName">
            <span class="model-label">{{ t('AI模型') }}:</span>
            <el-tag size="small" type="success" effect="light">{{ modelName }}</el-tag>
          </div>
          <div class="session-info">
            {{ t('会话ID') }}: {{ sessionId }}
            <span :class="['status-indicator', isConnected ? 'status-connected' : 'status-disconnected']"></span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧需求输入面板 -->
      <aside class="left-panel">
        <section class="requirement-panel">
          <h3>📝 {{ t('需求输入') }}</h3>

          <!-- 需求模板选择 -->
          <div class="template-section">
            <el-form-item :label="t('需求模板')">
              <el-select
                v-model="selectedTemplate"
                :placeholder="t('选择需求模板')"
                @change="applyTemplate"
                style="width: 100%;"
              >
                <el-option
                  v-for="template in requirementTemplates"
                  :key="template.id"
                  :label="template.name"
                  :value="template.id"
                />
              </el-select>
            </el-form-item>
          </div>

          <!-- 需求标题 -->
          <el-form-item :label="t('需求标题')">
            <el-input
              v-model="requirementData.title"
              :placeholder="t('请输入需求标题')"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>

  
          <!-- 附加参数 -->
          <div class="additional-params">
            <el-form-item :label="t('测试类型')">
              <el-select v-model="requirementData.testType" :placeholder="t('选择测试类型')">
                <el-option :label="t('功能测试')" value="functional" />
                <el-option :label="t('性能测试')" value="performance" />
                <el-option :label="t('安全测试')" value="security" />
                <el-option :label="t('兼容性测试')" value="compatibility" />
                <el-option :label="t('用户体验测试')" value="ux" />
              </el-select>
            </el-form-item>

            <el-form-item :label="t('优先级')">
              <el-select v-model="requirementData.priority" :placeholder="t('选择优先级')">
                <el-option :label="t('高')" value="high" />
                <el-option :label="t('中')" value="medium" />
                <el-option :label="t('低')" value="low" />
              </el-select>
            </el-form-item>

            <el-form-item :label="t('预估复杂度')">
              <el-tooltip
                placement="top"
                :show-after="500"
                :enterable="false"
              >
                <template #content>
                  <div style="max-width: 300px; line-height: 1.6;">
                    <div v-if="requirementData.complexity === 'simple'">
                      <strong>{{ t('简单复杂度') }}</strong><br>
                      {{ t('生成单个测试用例，包含3-4个核心测试步骤，覆盖主要功能点') }}
                    </div>
                    <div v-else-if="requirementData.complexity === 'medium'">
                      <strong>{{ t('中等复杂度') }}</strong><br>
                      {{ t('生成单个测试用例，包含5-6个测试步骤，包含正常流程和基本异常场景') }}
                    </div>
                    <div v-else-if="requirementData.complexity === 'complex'">
                      <strong>{{ t('复杂复杂度') }}</strong><br>
                      {{ t('生成2-4个相关测试用例，分别关注基本功能验证、异常场景处理、边界条件测试等') }}
                    </div>
                    <div v-else>
                      <strong>{{ t('复杂度说明') }}</strong><br>
                      • {{ t('简单') }}: {{ t('单个测试用例，3-4步') }}<br>
                      • {{ t('中等') }}: {{ t('单个测试用例，5-6步') }}<br>
                      • {{ t('复杂') }}: {{ t('多个测试用例，分组覆盖') }}
                    </div>
                  </div>
                </template>
                <el-select v-model="requirementData.complexity" :placeholder="t('选择复杂度')">
                  <el-option :label="t('简单')" value="simple" />
                  <el-option :label="t('中等')" value="medium" />
                  <el-option :label="t('复杂')" value="complex" />
                </el-select>
              </el-tooltip>
            </el-form-item>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <div class="main-actions">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :show-file-list="false"
                accept=".txt,.md,.json"
                :on-change="handleFileUpload"
                :before-upload="beforeFileUpload"
              >
                <el-button type="primary" plain>
                  📁 {{ t('加载需求文件') }}
                </el-button>
              </el-upload>

              <el-button type="primary" @click="parseRequirement" :loading="isParsing">
                🔍 {{ t('解析需求') }}
              </el-button>

              <el-button type="success" @click="generateTestCase" :loading="isGenerating" :disabled="!parsedRequirement">
                🚀 {{ t('生成测试用例') }}
              </el-button>
            </div>

            <div class="reset-action">
              <el-button @click="resetForm">
                🔄 {{ t('重置') }}
              </el-button>
            </div>
          </div>
        </section>

        <!-- 生成的测试用例列表 -->
        <section class="testcase-list-panel" v-if="generatedTestCases.length > 0">
          <h3>📋 {{ t('生成的测试用例') }}
            <span style="font-size: 14px; color: #666; font-weight: normal;">
              ({{ generatedTestCases.length }} {{ t('个') }})
            </span>
          </h3>

          <!-- 测试用例分组显示 -->
          <div v-if="testCasesGroups.length > 0" class="testcase-groups">
            <div
              v-for="group in testCasesGroups"
              :key="group.requirement_id"
              class="testcase-group"
            >
              <div class="group-header">
                <el-tag type="success" size="small">
                  📦 {{ t('需求组') }}
                </el-tag>
                <span class="group-info">{{ group.test_cases.length }} {{ t('个测试用例') }}</span>
                <el-tooltip :content="group.coverage_note" placement="top">
                  <el-icon class="info-icon"><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <div class="group-testcases">
                <el-card
                  v-for="testCase in group.test_cases"
                  :key="testCase.id"
                  :class="['testcase-item', { selected: selectedTestCase?.id === testCase.id }]"
                  @click="selectTestCase(testCase)"
                  shadow="hover"
                >
                  <div class="testcase-header">
                    <strong>{{ testCase.name }}</strong>
                    <div class="testcase-badges">
                      <el-tag :type="getPriorityType(testCase.priority)" size="small">
                        {{ t(testCase.priority) }}
                      </el-tag>
                      <el-tag v-if="testCase.coverage_aspect" type="info" size="small">
                        {{ testCase.coverage_aspect }}
                      </el-tag>
                    </div>
                  </div>
                  <p class="testcase-description">{{ testCase.objective }}</p>
                  <div class="testcase-meta">
                    <span class="testcase-steps">{{ testCase.steps?.length || 0 }} {{ t('个步骤') }}</span>
                    <span class="testcase-time">{{ formatTime(testCase.created_at) }}</span>
                  </div>
                </el-card>
              </div>
            </div>
          </div>

          <!-- 单个测试用例显示 -->
          <div v-if="hasSingleTestCases" class="single-testcases">
            <h4 v-if="testCasesGroups.length > 0">{{ t('其他测试用例') }}</h4>
            <div class="testcase-list">
              <el-card
                v-for="testCase in singleTestCases"
                :key="testCase.id"
                :class="['testcase-item', { selected: selectedTestCase?.id === testCase.id }]"
                @click="selectTestCase(testCase)"
                shadow="hover"
              >
                <div class="testcase-header">
                  <strong>{{ testCase.name }}</strong>
                  <div class="testcase-badges">
                    <el-tag :type="getPriorityType(testCase.priority)" size="small">
                      {{ t(testCase.priority) }}
                    </el-tag>
                    <el-tag v-if="testCase.coverage_aspect" type="info" size="small">
                      {{ testCase.coverage_aspect }}
                    </el-tag>
                  </div>
                </div>
                <p class="testcase-description">{{ testCase.objective }}</p>
                <div class="testcase-meta">
                  <span class="testcase-steps">{{ testCase.steps?.length || 0 }} {{ t('个步骤') }}</span>
                  <span class="testcase-time">{{ formatTime(testCase.created_at) }}</span>
                </div>
              </el-card>
            </div>
          </div>
        </section>
      </aside>

      <!-- 右侧内容区域 -->
      <main class="content-area">
        <!-- 需求描述面板 -->
        <section class="requirement-description-panel">
          <div class="panel-header">
            <h3>📄 {{ t('需求描述') }}
              <span style="color: #409eff; font-size: 14px; font-weight: normal;">
                - {{ requirementData.title || t('未命名需求') }}
              </span>
            </h3>
            <div class="panel-actions">
              <div class="requirement-tabs">
                <el-button
                  size="small"
                  :type="isEditingRequirement ? 'primary' : 'default'"
                  @click="toggleEditRequirement"
                >
                  {{ isEditingRequirement ? '✏️ ' + t('编辑中') : '📝 ' + t('编辑') }}
                </el-button>
                <el-button
                  size="small"
                  :type="requirementLanguage === 'markdown' ? 'primary' : 'default'"
                  @click="requirementLanguage = 'markdown'"
                >
                  Markdown
                </el-button>
                <el-button
                  size="small"
                  :type="requirementLanguage === 'plaintext' ? 'primary' : 'default'"
                  @click="requirementLanguage = 'plaintext'"
                >
                  {{ t('纯文本') }}
                </el-button>
              </div>
              <div v-if="requirementData.description" style="color: #666; font-size: 12px; margin-left: 10px;">
                📊 {{ requirementStats.characters }} {{ t('字符') }} | {{ requirementStats.lines }} {{ t('行') }}
              </div>
              <div v-else style="color: #999; font-size: 12px; margin-left: 10px;">
                💡 {{ t('点击下方区域开始编辑需求描述') }}
              </div>
            </div>
          </div>

          <div class="requirement-display">
            <!-- 编辑模式 -->
            <div v-if="isEditingRequirement" class="requirement-edit-mode">
              <el-input
                v-model="editedRequirement"
                type="textarea"
                :rows="12"
                :placeholder="t('请输入详细的需求描述...')"
                maxlength="5000"
                show-word-limit
                class="requirement-textarea"
              />
              <div class="requirement-edit-actions">
                <el-button size="small" type="success" @click="saveRequirementEdit">
                  💾 {{ t('保存') }}
                </el-button>
                <el-button size="small" @click="cancelRequirementEdit">
                  ❌ {{ t('取消') }}
                </el-button>
              </div>
            </div>

            <!-- 显示模式 -->
            <div
              v-else
              class="requirement-content-display"
              :class="{
                'language-markdown': requirementLanguage === 'markdown',
                'language-plaintext': requirementLanguage === 'plaintext',
                'empty-content': !requirementData.description
              }"
              @click="!requirementData.description && toggleEditRequirement()"
            >
              <div v-if="requirementData.description" v-html="highlightedRequirementContent"></div>
              <div v-else class="empty-content-hint">
                <p>{{ t('📝 请输入需求描述...') }}</p>
                <p style="font-size: 12px; color: #999;">{{ t('点击此处开始编辑，或使用上方加载文件按钮导入需求') }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 用户提示词面板 -->
        <section class="user-prompt-panel">
          <div class="panel-header">
            <h3>💡 {{ t('用户提示词') }}
              <el-tooltip :content="t('指定当前需求的特定提示词，可以指定特定的测试要求、格式或特殊场景')" placement="top">
                <el-icon class="help-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </h3>
            <div class="panel-actions">
              <el-button
                size="small"
                :type="isEditingUserPrompt ? 'primary' : 'default'"
                @click="toggleEditUserPrompt"
              >
                {{ isEditingUserPrompt ? '✏️ ' + t('编辑中') : '📝 ' + t('编辑') }}
              </el-button>
              <div v-if="userPrompt" style="color: #666; font-size: 12px; margin-left: 10px;">
                📝 {{ userPrompt.length }} {{ t('字符') }}
              </div>
              <div v-else style="color: #999; font-size: 12px; margin-left: 10px;">
                💡 {{ t('可选，补充特定要求') }}
              </div>
            </div>
          </div>

          <div class="user-prompt-display">
            <!-- 编辑模式 -->
            <div v-if="isEditingUserPrompt" class="user-prompt-edit-mode">
              <el-input
                v-model="editedUserPrompt"
                type="textarea"
                :rows="6"
                :placeholder="t('请输入额外的提示词，例如：\n- 重点关注安全相关的测试用例\n- 包含异常场景和边界条件测试\n- 测试步骤要详细具体\n- 输出格式为JSON\n...')"
                maxlength="2000"
                show-word-limit
                class="user-prompt-textarea"
              />

              <!-- 预设模板按钮 -->
              <div class="prompt-templates-section">
                <p style="margin: 8px 0; color: #666; font-size: 13px;">{{ t('快速模板:') }}</p>
                <div class="template-buttons" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px;">
                  <el-button
                    size="small"
                    type="primary"
                    plain
                    @click="applyPromptTemplate('english')"
                    style="font-size: 12px;"
                  >
                    🌍 {{ t('使用英文生成') }}
                  </el-button>
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="applyPromptTemplate('detailed')"
                    style="font-size: 12px;"
                  >
                    📋 {{ t('详细步骤') }}
                  </el-button>
                  <el-button
                    size="small"
                    type="warning"
                    plain
                    @click="applyPromptTemplate('security')"
                    style="font-size: 12px;"
                  >
                    🔒 {{ t('安全测试') }}
                  </el-button>
                  <el-button
                    size="small"
                    type="info"
                    plain
                    @click="applyPromptTemplate('boundary')"
                    style="font-size: 12px;"
                  >
                    🎯 {{ t('边界条件') }}
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    plain
                    @click="applyPromptTemplate('negative')"
                    style="font-size: 12px;"
                  >
                    ⚠️ {{ t('异常场景') }}
                  </el-button>
                </div>
              </div>

              <div class="user-prompt-edit-actions">
                <el-button size="small" type="success" @click="saveUserPromptEdit">
                  💾 {{ t('保存') }}
                </el-button>
                <el-button size="small" @click="cancelUserPromptEdit">
                  ❌ {{ t('取消') }}
                </el-button>
                <el-button size="small" @click="clearUserPrompt">
                  🗑️ {{ t('清空') }}
                </el-button>
              </div>
            </div>

            <!-- 显示模式 -->
            <div
              v-else
              class="user-prompt-content-display"
              @click="toggleEditUserPrompt()"
            >
              <div v-if="userPrompt" class="user-prompt-content">
                <div class="prompt-text">{{ userPrompt }}</div>
              </div>
              <div v-else class="empty-user-prompt">
                <p>{{ t('💡 添加用户提示词...') }}</p>
                <p style="font-size: 12px; color: #999;">{{ t('点击此处编辑，补充当前需求的特定要求') }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 解析结果面板 -->
        <section class="parse-result-panel" v-if="parsedRequirement">
          <div class="panel-header">
            <h3>🔍 {{ isEditingParsed ? `✏️ ${t('编辑解析结果')}` : t('解析结果') }}
              <span v-if="isEditingParsed ? editedParsedRequirement : parsedRequirement" style="color: #409eff; font-size: 14px; font-weight: normal;">
                {{ getDisplayTitle }}
              </span>
            </h3>
            <div class="panel-actions">
              <template v-if="isEditingParsed">
                <el-button size="small" type="success" @click="saveParsedRequirement">
                  💾 {{ t('保存') }}
                </el-button>
                <el-button size="small" @click="cancelEditParsedRequirement">
                  ❌ {{ t('取消') }}
                </el-button>
              </template>
              <template v-else>
                <el-button size="small" @click="editParsedRequirement">
                  ✏️ {{ t('编辑') }}
                </el-button>
                <el-button size="small" type="success" @click="regenerateTestCase">
                  🔄 {{ t('重新生成') }}
                </el-button>
              </template>
            </div>
          </div>

          <div class="parsed-content">
            <!-- 多测试用例解析结果 -->
            <div v-if="(isEditingParsed ? editedParsedRequirement : parsedRequirement)?.test_cases" class="multiple-testcases-preview">
              <div class="coverage-info">
                <h5>{{ t('覆盖说明') }}</h5>
                <el-input
                  v-if="isEditingParsed"
                  v-model="editedParsedRequirement.coverage_note"
                  type="textarea"
                  :rows="2"
                  :placeholder="t('请输入覆盖说明')"
                />
                <p v-else>{{ (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.coverage_note }}</p>
              </div>

              <div class="testcases-preview">
                <h5>{{ t('预览测试用例') }} ({{ (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.test_cases?.length || 0 }})</h5>
                <div
                  v-for="(testCase, index) in (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.test_cases || []"
                  :key="index"
                  class="testcase-preview-item"
                >
                  <div class="testcase-preview-header">
                    <el-input
                      v-if="isEditingParsed"
                      v-model="testCase.name"
                      size="small"
                      style="flex: 1; margin-right: 8px;"
                    />
                    <strong v-else>{{ testCase.name }}</strong>
                    <div class="testcase-preview-badges">
                      <el-select v-if="isEditingParsed" v-model="testCase.priority" size="small" style="width: 80px;">
                        <el-option :label="t('高')" value="high" />
                        <el-option :label="t('中')" value="medium" />
                        <el-option :label="t('低')" value="low" />
                      </el-select>
                      <el-tag v-else :type="getPriorityType(testCase.priority)" size="small">
                        {{ t(testCase.priority) }}
                      </el-tag>
                      <el-input
                        v-if="isEditingParsed"
                        v-model="testCase.coverage_aspect"
                        size="small"
                        style="width: 120px; margin-left: 4px;"
                        :placeholder="t('覆盖方面')"
                      />
                      <el-tag v-else-if="testCase.coverage_aspect" type="info" size="small">
                        {{ testCase.coverage_aspect }}
                      </el-tag>
                      <el-button
                        v-if="!isEditingParsed"
                        size="small"
                        type="primary"
                        plain
                        @click="editIndividualTestCase(testCase, index)"
                        style="margin-left: 8px;"
                      >
                        ✏️ {{ t('详情') }}
                      </el-button>
                    </div>
                  </div>
                  <el-input
                    v-if="isEditingParsed"
                    v-model="testCase.objective"
                    type="textarea"
                    :rows="2"
                    size="small"
                    class="testcase-preview-objective-edit"
                  />
                  <p v-else class="testcase-preview-objective">{{ testCase.objective }}</p>
                  <div class="testcase-preview-meta">
                    <span>{{ testCase.steps?.length || 0 }} {{ t('个步骤') }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 单个测试用例解析结果 -->
            <div v-else class="single-testcase-preview">
              <el-form :model="isEditingParsed ? editedParsedRequirement : parsedRequirement || {}" label-width="120px">
                <el-form-item :label="t('测试用例名称')">
                  <el-input v-if="isEditingParsed" v-model="editedParsedRequirement.name" />
                  <span v-else>{{ (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.name }}</span>
                </el-form-item>
                <el-form-item :label="t('测试目标')">
                  <el-input v-if="isEditingParsed" v-model="editedParsedRequirement.objective" type="textarea" :rows="2" />
                  <span v-else>{{ (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.objective }}</span>
                </el-form-item>
                <el-form-item :label="t('前置条件')">
                  <el-input v-if="isEditingParsed" v-model="editedParsedRequirement.preconditions" type="textarea" :rows="2" />
                  <span v-else>{{ (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.preconditions }}</span>
                </el-form-item>
              </el-form>

              <!-- 测试步骤 -->
              <div class="steps-section">
                <h4>{{ t('测试步骤') }}</h4>
                <div class="steps-list">
                  <div
                    v-for="(step, index) in (isEditingParsed ? editedParsedRequirement : parsedRequirement)?.steps || []"
                    :key="index"
                    class="step-item"
                  >
                    <div class="step-header">
                      <span class="step-number">{{ index + 1 }}</span>
                      <el-button v-if="isEditingParsed" size="small" type="danger" @click="removeStep(index)">
                        🗑️
                      </el-button>
                    </div>
                    <el-input
                      v-if="isEditingParsed"
                      v-model="step.test_step"
                      :placeholder="t('测试步骤')"
                      class="step-input"
                    />
                    <div v-else class="step-display">
                      <strong>{{ step.test_step }}</strong>
                    </div>
                    <el-input
                      v-if="isEditingParsed"
                      v-model="step.description"
                      :placeholder="t('详细描述')"
                      type="textarea"
                      :rows="2"
                      class="step-description"
                    />
                    <div v-else class="step-display">
                      {{ step.description }}
                    </div>
                    <el-input
                      v-if="isEditingParsed"
                      v-model="step.expected_result"
                      :placeholder="t('预期结果')"
                      class="step-expected"
                    />
                    <div v-else class="step-display">
                      <em>{{ step.expected_result }}</em>
                    </div>
                  </div>
                  <el-button v-if="isEditingParsed" @click="addStep" type="primary" plain>
                    ➕ {{ t('添加步骤') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 测试用例显示区域 -->
        <section class="testcase-display" v-if="selectedTestCase">
          <div class="panel-header">
            <h3>📄 {{ t('测试用例详情') }}
              <span style="color: #409eff; font-size: 14px; font-weight: normal;">
                - {{ selectedTestCase.name }}
              </span>
            </h3>
            <div class="panel-actions">
              <el-button @click="exportTestCase('json')">
                📄 {{ t('导出JSON') }}
              </el-button>
              <el-button @click="exportTestCase('markdown')">
                📝 {{ t('导出Markdown') }}
              </el-button>
              <el-button @click="exportTestCase('excel')">
                📊 {{ t('导出Excel') }}
              </el-button>
              <el-button @click="copyTestCase">
                📋 {{ t('复制') }}
              </el-button>
            </div>
          </div>

          <div class="testcase-content">
            <div class="testcase-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item :label="t('用例ID')">{{ selectedTestCase.id }}</el-descriptions-item>
                <el-descriptions-item :label="t('用例名称')">{{ selectedTestCase.name }}</el-descriptions-item>
                <el-descriptions-item :label="t('测试目标')">{{ selectedTestCase.objective }}</el-descriptions-item>
                <el-descriptions-item :label="t('优先级')">
                  <el-tag :type="getPriorityType(selectedTestCase.priority)">
                    {{ t(selectedTestCase.priority) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item :label="t('前置条件')" :span="2">
                  {{ selectedTestCase.preconditions }}
                </el-descriptions-item>
                <el-descriptions-item :label="t('创建时间')" :span="2">
                  {{ formatTime(selectedTestCase.created_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 测试步骤详情 -->
            <div class="testcase-steps">
              <h4>{{ t('测试步骤') }}</h4>
              <el-table :data="selectedTestCase.steps" style="width: 100%">
                <el-table-column prop="test_step" :label="t('测试步骤')" width="200" />
                <el-table-column prop="description" :label="t('详细描述')" />
                <el-table-column prop="expected_result" :label="t('预期结果')" width="200" />
              </el-table>
            </div>
          </div>
        </section>

        <!-- 加载和错误状态 -->
        <div v-if="isParsing" class="loading horizontal-loading">
          <div class="loading-spinner"></div>
          <span class="loading-text">{{ t('正在解析需求...') }}</span>
        </div>

        <div v-if="isGenerating" class="loading horizontal-loading">
          <div class="loading-spinner"></div>
          <span class="loading-text">{{ t('正在生成测试用例...') }}</span>
        </div>

        <div v-if="errorMessage" class="error-message">
          <el-alert :title="errorMessage" type="error" show-icon />
        </div>
      </main>
    </div>

    <!-- 单个测试用例编辑对话框 -->
    <el-dialog
      v-model="isEditingIndividualTestCase"
      :title="`✏️ ${t('编辑测试用例详情')}: ${editingIndividualTestCase?.name || ''}`"
      width="80%"
      :before-close="cancelIndividualTestCaseEdit"
    >
      <div v-if="editingIndividualTestCase" class="individual-testcase-edit">
        <el-form :model="editingIndividualTestCase" label-width="100px">
          <!-- 基本信息 -->
          <el-form-item :label="t('测试用例名称')">
            <el-input v-model="editingIndividualTestCase.name" />
          </el-form-item>

          <el-form-item :label="t('测试目标')">
            <el-input
              v-model="editingIndividualTestCase.objective"
              type="textarea"
              :rows="3"
            />
          </el-form-item>

          <el-form-item :label="t('前置条件')">
            <el-input
              v-model="editingIndividualTestCase.preconditions"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <el-form-item :label="t('优先级')">
            <el-select v-model="editingIndividualTestCase.priority">
              <el-option :label="t('高')" value="high" />
              <el-option :label="t('中')" value="medium" />
              <el-option :label="t('低')" value="low" />
            </el-select>
          </el-form-item>

          <el-form-item :label="t('覆盖方面')">
            <el-input v-model="editingIndividualTestCase.coverage_aspect" />
          </el-form-item>
        </el-form>

        <!-- 测试步骤 -->
        <div class="test-steps-section">
          <div class="section-header">
            <h4>{{ t('测试步骤') }}</h4>
            <el-button size="small" type="primary" @click="addTestStep">
              ➕ {{ t('添加步骤') }}
            </el-button>
          </div>

          <div class="test-steps-list">
            <div
              v-for="(step, stepIndex) in editingIndividualTestCase.steps || []"
              :key="stepIndex"
              class="test-step-item"
            >
              <div class="step-header">
                <span class="step-number">{{ stepIndex + 1 }}.</span>
                <el-button
                  size="small"
                  type="danger"
                  plain
                  @click="removeTestStep(stepIndex)"
                  class="remove-step-btn"
                >
                  🗑️ {{ t('删除') }}
                </el-button>
              </div>

              <div class="step-content">
                <el-form-item :label="t('测试步骤')">
                  <el-input
                    v-model="step.test_step"
                    type="textarea"
                    :rows="2"
                    :placeholder="t('请输入测试步骤描述')"
                  />
                </el-form-item>

                <el-form-item :label="t('详细描述')">
                  <el-input
                    v-model="step.description"
                    type="textarea"
                    :rows="2"
                    :placeholder="t('请输入详细操作描述')"
                  />
                </el-form-item>

                <el-form-item :label="t('预期结果')">
                  <el-input
                    v-model="step.expected_result"
                    type="textarea"
                    :rows="2"
                    :placeholder="t('请输入预期结果')"
                  />
                </el-form-item>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="cancelIndividualTestCaseEdit">{{ t('取消') }}</el-button>
        <el-button type="primary" @click="saveIndividualTestCaseEdit">{{ t('保存') }}</el-button>
      </template>
    </el-dialog>

    <!-- 使用说明弹窗 -->
    <el-dialog
      v-model="isUserGuideVisible"
      :title="t('使用说明')"
      width="80%"
      :before-close="closeUserGuide"
      class="user-guide-dialog"
    >
      <div class="user-guide-content">
        <el-collapse v-model="activeGuideSections" accordion>
          <!-- 快速开始 -->
          <el-collapse-item :title="t('🚀 快速开始')" name="quickstart">
            <div class="guide-section">
              <h4>{{ t('第一步：输入需求') }}</h4>
              <p>{{ t('在左侧"需求输入"面板中，填写需求标题，然后选择一个预设模板或直接输入详细的需求描述。') }}</p>

              <h4>{{ t('第二步：设置参数') }}</h4>
              <p>{{ t('选择测试类型（功能测试、性能测试等）、优先级和预估复杂度，这些参数会影响生成测试用例的范围和深度。') }}</p>

              <h4>{{ t('第三步：解析需求') }}</h4>
              <p>{{ t('点击"解析需求"按钮，系统会分析您的需求并提取测试用例的基本结构。') }}</p>

              <h4>{{ t('第四步：生成测试用例') }}</h4>
              <p>{{ t('解析完成后，点击"生成测试用例"按钮，系统将生成详细的测试用例。') }}</p>
            </div>
          </el-collapse-item>

          <!-- 功能说明 -->
          <el-collapse-item :title="t('📋 功能说明')" name="features">
            <div class="guide-section">
              <h4>{{ t('需求模板') }}</h4>
              <p>{{ t('系统提供了多种预设的需求模板，包括雨刷器测试、CAN通信测试、前大灯测试等，涵盖了汽车电子的常见测试场景。') }}</p>

              <h4>{{ t('用户提示词') }}</h4>
              <p>{{ t('可以在"用户提示词"区域补充特定的测试要求，比如指定输出格式、重点关注的安全测试等。') }}</p>

              <h4>{{ t('复杂度设置') }}</h4>
              <ul>
                <li><strong>{{ t('简单') }}</strong>: {{ t('生成单个测试用例，包含3-4个核心测试步骤') }}</li>
                <li><strong>{{ t('中等') }}</strong>: {{ t('生成单个测试用例，包含5-6个测试步骤，包含正常流程和基本异常场景') }}</li>
                <li><strong>{{ t('复杂') }}</strong>: {{ t('生成2-4个相关测试用例，分别关注基本功能验证、异常场景处理、边界条件测试等') }}</li>
              </ul>

              <h4>{{ t('文件导入') }}</h4>
              <p>{{ t('支持导入.txt、.md、.json格式的需求文档，快速填充需求描述内容。') }}</p>
            </div>
          </el-collapse-item>

          <!-- 编辑功能 -->
          <el-collapse-item :title="t('✏️ 编辑功能')" name="editing">
            <div class="guide-section">
              <h4>{{ t('需求描述编辑') }}</h4>
              <p>{{ t('点击"编辑"按钮可以直接修改需求描述，支持Markdown和纯文本格式。') }}</p>

              <h4>{{ t('解析结果编辑') }}</h4>
              <p>{{ t('解析完成后，可以编辑测试用例的名称、目标、前置条件和测试步骤。') }}</p>

              <h4>{{ t('测试用例详情编辑') }}</h4>
              <p>{{ t('对于复杂需求生成的多测试用例，可以点击"详情"按钮单独编辑每个测试用例的详细内容。') }}</p>
            </div>
          </el-collapse-item>

          <!-- 导出功能 -->
          <el-collapse-item :title="t('📤 导出功能')" name="export">
            <div class="guide-section">
              <h4>{{ t('支持的导出格式') }}</h4>
              <ul>
                <li><strong>{{ t('JSON格式') }}</strong>: {{ t('包含完整的测试用例数据，便于系统集成和二次开发') }}</li>
                <li><strong>{{ t('Markdown格式') }}</strong>: {{ t('适合文档编写和版本控制') }}</li>
                <li><strong>{{ t('Excel格式') }}</strong>: {{ t('包含基本信息和测试步骤两个工作表，便于测试管理') }}</li>
              </ul>

              <h4>{{ t('批量导出') }}</h4>
              <p>{{ t('选择任意测试用例后，可以使用导出功能将测试用例保存为不同格式的文件。') }}</p>
            </div>
          </el-collapse-item>

          <!-- 提示词模板 -->
          <el-collapse-item :title="t('💡 提示词模板')" name="prompts">
            <div class="guide-section">
              <h4>{{ t('快速模板功能') }}</h4>
              <p>{{ t('在用户提示词编辑区域，提供了多种快速模板按钮：') }}</p>
              <ul>
                <li><strong>{{ t('使用英文生成') }}</strong>: {{ t('生成英文格式的测试用例') }}</li>
                <li><strong>{{ t('详细步骤') }}</strong>: {{ t('生成非常详细的测试步骤，包含具体操作和验证方法') }}</li>
                <li><strong>{{ t('安全测试') }}</strong>: {{ t('专注于安全相关的测试场景') }}</li>
                <li><strong>{{ t('边界条件') }}</strong>: {{ t('包含全面的边界条件测试') }}</li>
                <li><strong>{{ t('异常场景') }}</strong>: {{ t('包含负面测试和异常处理场景') }}</li>
              </ul>
            </div>
          </el-collapse-item>

          <!-- 故障排除 -->
          <el-collapse-item :title="t('🔧 故障排除')" name="troubleshooting">
            <div class="guide-section">
              <h4>{{ t('连接失败') }}</h4>
              <p>{{ t('如果右上角的状态指示器显示为红色，表示后端服务连接失败。请检查服务是否正常运行。') }}</p>

              <h4>{{ t('生成失败') }}</h4>
              <p>{{ t('如果测试用例生成失败，请检查：') }}</p>
              <ul>
                <li>{{ t('需求描述是否足够详细和清晰') }}</li>
                <li>{{ t('网络连接是否正常') }}</li>
                <li>{{ t('用户提示词是否包含矛盾的要求') }}</li>
              </ul>

              <h4>{{ t('内容优化建议') }}</h4>
              <ul>
                <li>{{ t('需求描述应该包含具体的功能要求和测试条件') }}</li>
                <li>{{ t('明确测试目标和验收标准') }}</li>
                <li>{{ t('提供相关的技术规格和约束条件') }}</li>
              </ul>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <template #footer>
        <el-button @click="closeUserGuide">{{ t('关闭') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, QuestionFilled, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import 'element-plus/dist/index.css'
import 'highlight.js/styles/github.css'
import hljs from 'highlight.js/lib/core'
import markdown from 'highlight.js/lib/languages/markdown'
import { useLanguageStore } from '../stores/language'
import * as XLSX from 'xlsx'

// 注册语言
hljs.registerLanguage('markdown', markdown)

// API基础URL配置
const API_BASE_URL = '/api'

// 语言store
const languageStore = useLanguageStore()
const { t, toggleLanguage } = languageStore

// 类型定义
interface RequirementTemplate {
  id: string
  name: string
  description: string
  template: string
  testType: string
  priority: string
  complexity: string
}

interface RequirementData {
  title: string
  description: string
  testType: string
  priority: string
  complexity: string
  userPrompt?: string
}

interface ParsedRequirement {
  id?: string
  name?: string
  objective?: string
  preconditions?: string
  steps?: Array<{
    test_step: string
    description: string
    expected_result: string
    timestamp: string
  }>
  test_cases?: Array<{
    name: string
    objective: string
    preconditions: string
    test_type: string
    priority: string
    coverage_aspect?: string
    steps: Array<{
      test_step: string
      description: string
      expected_result: string
    }>
  }>
  requirement_id?: string
  coverage_note?: string
}

interface GeneratedTestCase {
  id: string
  name: string
  objective: string
  preconditions: string
  priority: string
  test_type: string
  coverage_aspect?: string
  requirement_id?: string
  steps: Array<{
    test_step: string
    description: string
    expected_result: string
    timestamp: string
  }>
  created_at: string
}

interface TestCasesGroup {
  requirement_id: string
  coverage_note: string
  test_cases: GeneratedTestCase[]
  created_at: string
}

// 响应式数据
const sessionId = ref<string>(localStorage.getItem('requirement_session_id') || 'session_' + Math.random().toString(36).substr(2, 9))
const isConnected = ref<boolean>(false)
const modelName = ref<string>('')
const selectedTemplate = ref<string>('')
const requirementLanguage = ref<'markdown' | 'plaintext'>('markdown')
const isParsing = ref<boolean>(false)
const isGenerating = ref<boolean>(false)
const errorMessage = ref<string>('')
const parsedRequirement = ref<ParsedRequirement | null>(null)
const selectedTestCase = ref<GeneratedTestCase | null>(null)
const generatedTestCases = ref<GeneratedTestCase[]>([])
const testCasesGroups = ref<TestCasesGroup[]>([])
const uploadRef = ref<any>(null)
const isUploading = ref<boolean>(false)
const isEditingParsed = ref<boolean>(false)
const editedParsedRequirement = ref<ParsedRequirement | null>(null)
const isEditingRequirement = ref<boolean>(false)
const editedRequirement = ref<string>('')
const userPrompt = ref<string>('')
const isEditingUserPrompt = ref<boolean>(false)
const editedUserPrompt = ref<string>('')

// 单个测试用例编辑相关
const isEditingIndividualTestCase = ref<boolean>(false)
const editingIndividualTestCase = ref<any>(null)
const editingTestCaseIndex = ref<number>(-1)

// 使用说明弹窗相关
const isUserGuideVisible = ref<boolean>(false)
const activeGuideSections = ref<string>('quickstart')

// 表单数据
const requirementData = reactive<RequirementData>({
  title: '',
  description: '',
  testType: 'functional',
  priority: 'medium',
  complexity: 'medium',
  userPrompt: ''
})

// 需求模板数据
const requirementTemplates = ref<RequirementTemplate[]>([
  {
    id: 'wiper_test',
    name: t('雨刷器功能测试'),
    description: t('验证车辆雨刷器各项功能的正常工作'),
    template: `# ${t('雨刷器功能测试需求')}

## ${t('测试目标')}
${t('验证车辆雨刷器在不同档位和工况下的正常工作状态，包括间歇模式、低速模式、高速模式以及自动感应模式。')}

## ${t('功能要求')}
1. ${t('雨刷器能够正常启动和停止')}
2. ${t('各档位速度切换正常')}
3. ${t('间歇模式时间间隔准确')}
4. ${t('自动雨量感应功能正常')}
5. ${t('回位功能正常')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('雨刷器电机工作正常')}
- ${t('雨量传感器工作正常')}
- ${t('相关控制模块无故障码')}`,
    testType: 'functional',
    priority: 'high',
    complexity: 'medium'
  },
  {
    id: 'can_communication',
    name: t('CAN通信测试'),
    description: t('验证CAN总线通信的正确性和稳定性'),
    template: `# ${t('CAN通信测试需求')}

## ${t('测试目标')}
${t('验证ECU之间CAN总线通信的稳定性、数据传输准确性和错误处理能力。')}

## ${t('通信要求')}
1. ${t('CAN总线波特率设置正确')}
2. ${t('消息ID配置正确')}
3. ${t('数据传输无丢失')}
4. ${t('错误帧处理正确')}
5. ${t('总线负载在合理范围')}

## ${t('测试条件')}
- ${t('CAN总线硬件连接正常')}
- ${t('各ECU供电正常')}
- ${t('终端电阻配置正确')}
- ${t('无外部电磁干扰')}`,
    testType: 'functional',
    priority: 'high',
    complexity: 'complex'
  },
  {
    id: 'performance_test',
    name: t('系统性能测试'),
    description: t('验证系统在不同负载下的性能表现'),
    template: `# ${t('系统性能测试需求')}

## ${t('测试目标')}
${t('验证系统在高负载、长时间运行情况下的性能表现，包括响应时间、资源利用率和稳定性。')}

## ${t('性能要求')}
1. ${t('系统响应时间 < 100ms')}
2. ${t('CPU利用率 < 80%')}
3. ${t('内存利用率 < 90%')}
4. ${t('24小时连续运行无故障')}
5. ${t('支持并发用户数 > 100')}

## ${t('测试条件')}
- ${t('系统硬件配置满足要求')}
- ${t('网络连接稳定')}
- ${t('测试数据准备充分')}`,
    testType: 'performance',
    priority: 'medium',
    complexity: 'complex'
  },
  {
    id: 'headlight_test',
    name: t('前大灯系统测试'),
    description: t('验证车辆前大灯各项功能的正常工作'),
    template: `# ${t('前大灯系统测试需求')}

## ${t('测试目标')}
${t('验证车辆前大灯系统在不同工作模式下的正常功能，包括近光灯、远光灯、转向灯、日间行车灯以及自动灯光控制。')}

## ${t('功能要求')}
1. ${t('近光灯和远光灯切换正常')}
2. ${t('转向灯闪烁频率符合标准（每分钟90-120次）')}
3. ${t('日间行车灯自动点亮和熄灭')}
4. ${t('自动灯光感应器工作正常')}
5. ${t('大灯水平调节功能正常')}
6. ${t('随动转向大灯功能正常（如配备）')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('车身控制模块(BCM)工作正常')}
- ${t('灯光传感器工作正常')}
- ${t('相关保险丝和继电器正常')}
- ${t('无故障码存储')}`,
    testType: 'functional',
    priority: 'high',
    complexity: 'medium'
  },
  {
    id: 'taillight_test',
    name: t('尾灯系统测试'),
    description: t('验证车辆尾灯系统的各项功能'),
    template: `# ${t('尾灯系统测试需求')}

## ${t('测试目标')}
${t('验证车辆尾灯系统包括制动灯、倒车灯、后转向灯、雾灯等功能的正常工作。')}

## ${t('功能要求')}
1. ${t('制动灯在踩刹车时立即点亮')}
2. ${t('倒车灯在挂倒挡时正常点亮')}
3. ${t('后转向灯与前转向灯同步工作')}
4. ${t('后雾灯在能见度低时正常工作')}
5. ${t('LED尾灯亮度均匀，无闪烁')}
6. ${t('紧急制动时爆闪功能正常（如配备）')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('变速箱档位传感器正常')}
- ${t('制动开关信号正常')}
- ${t('尾灯控制模块无故障码')}
- ${t('灯泡/LED模块状态良好')}`,
    testType: 'functional',
    priority: 'high',
    complexity: 'medium'
  },
  {
    id: 'mirror_control_test',
    name: t('后视镜控制测试'),
    description: t('验证电动后视镜的各项调节功能'),
    template: `# ${t('后视镜控制测试需求')}

## ${t('测试目标')}
${t('验证车辆电动后视镜的调节功能、折叠功能、加热功能以及盲区监测功能的正常工作。')}

## ${t('功能要求')}
1. ${t('左右后视镜上下左右调节灵活')}
2. ${t('电动折叠/展开功能正常')}
3. ${t('后视镜加热在低温时自动启动')}
4. ${t('盲区监测报警准确及时')}
5. ${t('倒车时右侧后视镜自动下翻（如配备）')}
6. ${t('记忆座椅与后视镜位置联动正常')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('后视镜开关正常')}
- ${t('相关电机和传感器工作正常')}
- ${t('CAN总线通信正常')}
- ${t('环境温度传感器正常')}`,
    testType: 'functional',
    priority: 'medium',
    complexity: 'medium'
  },
  {
    id: 'window_control_test',
    name: t('车窗控制测试'),
    description: t('验证电动车窗的各项功能'),
    template: `# ${t('车窗控制测试需求')}

## ${t('测试目标')}
${t('验证车辆电动车窗的升降功能、防夹功能、一键升降功能以及遥控车窗功能的正常工作。')}

## ${t('功能要求')}
1. ${t('各车窗升降平稳无卡滞')}
2. ${t('防夹功能灵敏可靠，能及时停止并下降')}
3. ${t('一键升降功能响应准确')}
4. ${t('遥控钥匙可远程控制车窗')}
5. ${t('锁车自动升窗功能正常')}
6. ${t('车窗位置记忆功能正常（如配备）')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('车窗开关工作正常')}
- ${t('车窗电机状态良好')}
- ${t('防夹传感器工作正常')}
- ${t('车身控制模块无故障码')}`,
    testType: 'functional',
    priority: 'medium',
    complexity: 'simple'
  },
  {
    id: 'door_lock_test',
    name: t('车门门锁测试'),
    description: t('验证中央门锁系统的各项功能'),
    template: `# ${t('车门门锁测试需求')}

## ${t('测试目标')}
${t('验证车辆中央门锁系统的锁定/解锁功能、遥控功能、速度感应自动落锁以及儿童锁功能的正常工作。')}

## ${t('功能要求')}
1. ${t('遥控钥匙锁定/解锁所有车门')}
2. ${t('驾驶侧门锁开关控制所有车门')}
3. ${t('车速超过15km/h时自动落锁')}
4. ${t('P挡熄火后自动解锁')}
5. ${t('儿童锁功能有效防止后门从内部开启')}
6. ${t('门锁位置传感器反馈准确')}

## ${t('测试条件')}
- ${t('车辆电源正常')}
- ${t('遥控钥匙电池电量充足')}
- ${t('门锁执行器工作正常')}
- ${t('车速信号正常')}
- ${t('挡位传感器正常')}
- ${t('无门锁相关故障码')}`,
    testType: 'functional',
    priority: 'high',
    complexity: 'simple'
  },
  {
    id: 'functional_safety_monitoring',
    name: t('功能安全监控测试'),
    description: t('验证汽车功能安全监控系统的正常运行'),
    template: `# ${t('功能安全监控测试需求')}

## ${t('测试目标')}
${t('验证车辆功能安全监控系统按照ISO 26262标准要求，能够正确检测系统故障、执行安全状态转换，并确保车辆在故障情况下的安全运行。')}

## ${t('安全要求')}
1. ${t('故障检测机制能够及时识别系统异常')}
2. ${t('安全状态管理按照ASIL等级要求执行')}
3. ${t('冗余系统能够在主系统故障时接管控制')}
4. ${t('故障存储和诊断功能正常工作')}
5. ${t('系统重启和恢复机制符合安全要求')}
6. ${t('安全相关信号监控和超时检测正常')}

## ${t('测试条件')}
- ${t('车辆电源和接地系统正常')}
- ${t('安全ECU(如BMS、ESP、ECM)工作正常')}
- ${t('相关传感器和执行器状态良好')}
- ${t('诊断接口通信正常')}
- ${t('安全监控系统软件版本正确')}`,
    testType: 'security',
    priority: 'high',
    complexity: 'complex'
  },
  {
    id: 'brake_safety_system',
    name: t('制动系统安全测试'),
    description: t('验证制动系统的功能安全和故障容错'),
    template: `# ${t('制动系统安全测试需求')}

## ${t('测试目标')}
${t('验证车辆制动系统在各种工况下的功能安全性，包括ABS、ESC、制动助力失效等场景，确保制动性能符合功能安全要求。')}

## ${t('安全要求')}
1. ${t('ABS防抱死系统工作正常，防止车轮锁死')}
2. ${t('ESC电子稳定控制系统能够及时纠正车辆侧滑')}
3. ${t('紧急制动辅助系统提供最大制动力')}
4. ${t('制动力分配系统确保车辆稳定性')}
5. ${t('制动助力失效时提供足够的机械制动力')}
6. ${t('制动系统故障诊断和报警功能正常')}
7. ${t('自动紧急制动系统AEB功能符合预期')}

## ${t('测试条件')}
- ${t('制动液位和压力正常')}
- ${t('制动片和制动盘状态良好')}
- ${t('轮速传感器工作正常')}
- ${t('制动控制模块ECU无故障码')}
- ${t('车辆载荷在规定范围内')}
- ${t('测试路面附着力充足')}`,
    testType: 'security',
    priority: 'high',
    complexity: 'complex'
  },
  {
    id: 'powertrain_safety',
    name: t('动力系统安全测试'),
    description: t('验证动力系统的功能安全和故障处理'),
    template: `# ${t('动力系统安全测试需求')}

## ${t('测试目标')}
${t('验证车辆动力系统(发动机、电机、变速箱)在各种故障情况下的安全响应，确保车辆不会因动力系统故障而导致安全事故。')}

## ${t('安全要求')}
1. ${t('扭矩监控和限制功能正常工作')}
2. ${t('发动机/电机过载保护机制有效')}
3. ${t('变速箱故障保护模式正常启动')}
4. ${t('动力系统紧急停机功能安全可靠')}
5. ${t('油门踏板位置传感器故障检测正常')}
6. ${t('动力系统通信故障处理符合要求')}
7. ${t('混合动力系统高压安全保护有效')}

## ${t('测试条件')}
- ${t('发动机/电机温度和压力正常')}
- ${t('变速箱油位和温度在正常范围')}
- ${t('动力系统控制单元无故障码')}
- ${t('相关传感器信号准确有效')}
- ${t('车辆处于安全测试环境')}
- ${t('高压系统(如适用)绝缘良好')}`,
    testType: 'security',
    priority: 'high',
    complexity: 'complex'
  },
  {
    id: 'steering_safety_system',
    name: t('转向系统安全测试'),
    description: t('验证转向系统的功能安全和失效保护'),
    template: `# ${t('转向系统安全测试需求')}

## ${t('测试目标')}
${t('验证车辆转向系统的功能安全性，包括电动助力转向、转向角度控制、失效保护等，确保在任何情况下都能保持转向控制能力。')}

## ${t('安全要求')}
1. ${t('电动助力转向系统提供适当的转向助力')}
2. ${t('转向角度传感器精度和响应时间符合要求')}
3. ${t('转向系统失效时提供手动转向能力')}
4. ${t('车道保持辅助系统工作正常')}
5. ${t('自动紧急转向功能(如配备)安全可靠')}
6. ${t('转向系统故障诊断和报警功能正常')}
7. ${t('转向力矩传感器冗余配置有效')}

## ${t('测试条件')}
- ${t('转向系统液压/电力供应正常')}
- ${t('转向角度传感器校准准确')}
- ${t('车轮定位参数正确')}
- ${t('转向控制模块无故障码')}
- ${t('车辆静止或低速安全环境')}
- ${t('方向盘自由行程在规定范围内')}`,
    testType: 'security',
    priority: 'high',
    complexity: 'medium'
  },
  {
    id: 'battery_management_safety',
    name: t('电池管理系统安全测试'),
    description: t('验证电池管理系统的功能安全'),
    template: `# ${t('电池管理系统安全测试需求')}

## ${t('测试目标')}
${t('验证电池管理系统(BMS)的安全功能，包括过充保护、过放保护、热管理、绝缘监测等，确保高压电池系统的安全运行。')}

## ${t('安全要求')}
1. ${t('过充电保护机制及时阻止充电')}
2. ${t('过放电保护防止电池深度放电')}
3. ${t('电池温度监测和热管理功能正常')}
4. ${t('高压绝缘监测和漏电保护有效')}
5. ${t('电池均衡功能确保单体电池一致性')}
6. ${t('电池状态估算SOC/SOH精度满足要求')}
7. ${t('紧急断开和熔断保护机制可靠')}

## ${t('测试条件')}
- ${t('电池包温度在正常工作范围')}
- ${t('高压系统绝缘电阻符合标准')}
- ${t('BMS软件和固件版本正确')}
- ${t('相关传感器校准准确')}
- ${t('测试环境具备高压安全措施')}
- ${t('电池管理系统通信正常')}`,
    testType: 'security',
    priority: 'high',
    complexity: 'complex'
  }
])

// 生命周期
onMounted(() => {
  localStorage.setItem('requirement_session_id', sessionId.value)
  languageStore.initLanguage()
  checkHealth()
})

// 方法
const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`)
    isConnected.value = true
    modelName.value = response.data.model_name || ''
  } catch (_: any) {
    isConnected.value = false
    modelName.value = ''
    ElMessage.error(t('服务连接失败'))
  }
}

const applyTemplate = () => {
  const template = requirementTemplates.value.find(t => t.id === selectedTemplate.value)
  if (template) {
    requirementData.title = template.name
    requirementData.description = template.template
    requirementData.testType = template.testType
    requirementData.priority = template.priority
    requirementData.complexity = template.complexity
    ElMessage.success(t('已应用模板: ') + template.name)
  }
}

const parseRequirement = async () => {
  if (!requirementData.title.trim() || !requirementData.description.trim()) {
    ElMessage.warning(t('请填写需求标题和描述'))
    return
  }

  isParsing.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post(`${API_BASE_URL}/parse-requirement`, {
      title: requirementData.title,
      description: requirementData.description,
      test_type: requirementData.testType,
      priority: requirementData.priority,
      complexity: requirementData.complexity,
      user_prompt: requirementData.userPrompt,
      session_id: sessionId.value
    })

    if (response.data.error) {
      errorMessage.value = response.data.error
      ElMessage.error(t('需求解析失败: ') + response.data.error)
      return
    }

    parsedRequirement.value = response.data.parsed_requirement

    // 计算测试步骤数量（支持单个和多个测试用例格式）
    let totalSteps = 0
    if (parsedRequirement.value.test_cases) {
      // 多测试用例格式
      totalSteps = parsedRequirement.value.test_cases.reduce((sum: number, tc: any) => sum + (tc.steps?.length || 0), 0)
      ElMessage.success(t('需求解析完成，共生成 ') + parsedRequirement.value.test_cases.length + t('个测试用例，') + totalSteps + t('个测试步骤'))
    } else {
      // 单个测试用例格式
      totalSteps = parsedRequirement.value.steps?.length || 0
      ElMessage.success(t('需求解析完成，共提取 ') + totalSteps + t('个测试步骤'))
    }

  } catch (error: any) {
    console.error(t('解析失败: ') + error)
    errorMessage.value = error.response?.data?.detail || t('解析失败，请重试')
    ElMessage.error(t('需求解析失败'))
  } finally {
    isParsing.value = false
  }
}

const generateTestCase = async () => {
  if (!parsedRequirement.value) {
    ElMessage.warning(t('请先解析需求'))
    return
  }

  isGenerating.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post(`${API_BASE_URL}/generate-testcase`, {
      parsed_requirement: parsedRequirement.value,
      user_prompt: requirementData.userPrompt,
      session_id: sessionId.value
    })

    if (response.data.error) {
      errorMessage.value = response.data.error
      ElMessage.error(t('测试用例生成失败: ') + response.data.error)
      return
    }

    if (response.data.type === 'multiple') {
      // 处理多个测试用例
      const testCasesGroup: TestCasesGroup = {
        requirement_id: response.data.requirement_id,
        coverage_note: response.data.coverage_note,
        test_cases: response.data.test_cases.map((tc: any) => ({
          ...tc,
          created_at: new Date().toISOString()
        })),
        created_at: new Date().toISOString()
      }

      testCasesGroups.value.push(testCasesGroup)

      // 将所有测试用例添加到总列表中
      response.data.test_cases.forEach((tc: any) => {
        const newTestCase: GeneratedTestCase = {
          ...tc,
          created_at: new Date().toISOString()
        }
        generatedTestCases.value.push(newTestCase)
      })

      selectedTestCase.value = response.data.test_cases[0]
      ElMessage.success(t('成功生成') + response.data.test_cases.length + t('个测试用例'))
    } else {
      // 处理单个测试用例
      const newTestCase: GeneratedTestCase = {
        ...response.data.test_case,
        created_at: new Date().toISOString()
      }

      generatedTestCases.value.push(newTestCase)
      selectedTestCase.value = newTestCase
      ElMessage.success(t('测试用例生成完成: ') + newTestCase.name)
    }

  } catch (error: any) {
    console.error(t('生成失败: ') + error)
    errorMessage.value = error.response?.data?.detail || t('生成失败，请重试')
    ElMessage.error(t('测试用例生成失败'))
  } finally {
    isGenerating.value = false
  }
}

const selectTestCase = (testCase: GeneratedTestCase) => {
  selectedTestCase.value = testCase
}

// 单个测试用例编辑相关方法
const editIndividualTestCase = (testCase: any, index: number) => {
  // 深拷贝测试用例以避免直接修改原数据
  editingIndividualTestCase.value = JSON.parse(JSON.stringify(testCase))
  editingTestCaseIndex.value = index
  isEditingIndividualTestCase.value = true
}

const saveIndividualTestCaseEdit = () => {
  if (!editingIndividualTestCase.value || editingTestCaseIndex.value === -1) return

  // 更新原始数据中的测试用例
  if (editedParsedRequirement.value?.test_cases) {
    editedParsedRequirement.value.test_cases[editingTestCaseIndex.value] = editingIndividualTestCase.value
  } else if (parsedRequirement.value?.test_cases) {
    // 如果没有正在编辑的整体数据，直接更新原数据
    const sourceData = editedParsedRequirement.value || parsedRequirement.value
    if (sourceData?.test_cases) {
      sourceData.test_cases[editingTestCaseIndex.value] = editingIndividualTestCase.value
    }
  }

  ElMessage.success(t('测试用例已保存'))
  cancelIndividualTestCaseEdit()
}

const cancelIndividualTestCaseEdit = () => {
  isEditingIndividualTestCase.value = false
  editingIndividualTestCase.value = null
  editingTestCaseIndex.value = -1
}

const addTestStep = () => {
  if (!editingIndividualTestCase.value) return

  if (!editingIndividualTestCase.value.steps) {
    editingIndividualTestCase.value.steps = []
  }

  editingIndividualTestCase.value.steps.push({
    test_step: '',
    description: '',
    expected_result: ''
  })
}

const removeTestStep = (index: number) => {
  if (!editingIndividualTestCase.value?.steps) return

  editingIndividualTestCase.value.steps.splice(index, 1)
  ElMessage.success(t('步骤已删除'))
}

const resetForm = () => {
  requirementData.title = ''
  requirementData.description = ''
  requirementData.userPrompt = ''
  requirementData.testType = 'functional'
  requirementData.priority = 'medium'
  requirementData.complexity = 'medium'
  selectedTemplate.value = ''
  parsedRequirement.value = null
  selectedTestCase.value = null
  generatedTestCases.value = []
  testCasesGroups.value = []

  // 重置用户提示词相关状态
  userPrompt.value = ''
  editedUserPrompt.value = ''
  isEditingUserPrompt.value = false

  errorMessage.value = ''
  ElMessage.success(t('表单已重置'))
}


const toggleEditRequirement = () => {
  if (!isEditingRequirement.value) {
    // 进入编辑模式
    editedRequirement.value = requirementData.description
    isEditingRequirement.value = true
  } else {
    // 退出编辑模式
    isEditingRequirement.value = false
  }
}

const saveRequirementEdit = () => {
  if (!editedRequirement.value.trim()) {
    ElMessage.warning(t('需求描述不能为空'))
    return
  }

  requirementData.description = editedRequirement.value
  isEditingRequirement.value = false
  ElMessage.success(t('需求描述已保存'))
}

const cancelRequirementEdit = () => {
  editedRequirement.value = requirementData.description
  isEditingRequirement.value = false
  ElMessage.info(t('已取消编辑'))
}

const toggleEditUserPrompt = () => {
  if (!isEditingUserPrompt.value) {
    // 进入编辑模式
    editedUserPrompt.value = userPrompt.value
    isEditingUserPrompt.value = true
  } else {
    // 退出编辑模式
    isEditingUserPrompt.value = false
  }
}

const saveUserPromptEdit = () => {
  userPrompt.value = editedUserPrompt.value
  requirementData.userPrompt = editedUserPrompt.value
  isEditingUserPrompt.value = false
  ElMessage.success(t('用户提示词已保存'))
}

const cancelUserPromptEdit = () => {
  editedUserPrompt.value = userPrompt.value
  isEditingUserPrompt.value = false
  ElMessage.info(t('已取消编辑'))
}

const clearUserPrompt = () => {
  userPrompt.value = ''
  requirementData.userPrompt = ''
  editedUserPrompt.value = ''
  isEditingUserPrompt.value = false
  ElMessage.success(t('用户提示词已清空'))
}

const applyPromptTemplate = (templateType: string) => {
  const templates = {
    english: t('请用英文格式生成测试用例，所有内容包括测试步骤、描述和预期结果都使用英文。'),
    detailed: t('请生成非常详细的测试步骤，每个步骤应包括：\n- 要执行的具体操作\n- 详细的输入数据和参数\n- 清晰的预期结果\n- 验证方法\n- 如适用，时间要求'),
    security: t('请专注于安全相关测试，包括：\n- 身份验证和授权测试\n- 输入验证和SQL注入防护\n- XSS和CSRF保护测试\n- 数据加密和安全传输\n- 访问控制和权限提升测试'),
    boundary: t('请包含全面的边界条件测试：\n- 最小值和最大值\n- 空值、null和无效输入\n- 字符长度限制\n- 数值范围边界\n- 文件大小和格式限制\n- 并发用户限制'),
    negative: t('请包含负面测试场景：\n- 无效的输入格式\n- 缺少必填字段\n- 系统错误处理\n- 网络中断场景\n- 资源耗尽情况\n- 格式错误的请求和数据损坏')
  }

  const templateText = templates[templateType as keyof typeof templates]
  if (templateText) {
    editedUserPrompt.value = editedUserPrompt.value
      ? editedUserPrompt.value + '\n\n' + templateText
      : templateText
    ElMessage.success(t('模板已应用: ') + templateType)
  }
}

const editParsedRequirement = () => {
  if (!parsedRequirement.value) {
    ElMessage.warning(t('没有可编辑的解析结果'))
    return
  }

  // 深拷贝解析结果用于编辑
  editedParsedRequirement.value = JSON.parse(JSON.stringify(parsedRequirement.value))
  isEditingParsed.value = true
}

const saveParsedRequirement = () => {
  if (!editedParsedRequirement.value) {
    ElMessage.error(t('没有可保存的修改'))
    return
  }

  // 验证编辑后的内容
  if (editedParsedRequirement.value.test_cases) {
    // 多测试用例模式验证
    if (!editedParsedRequirement.value.test_cases || editedParsedRequirement.value.test_cases.length === 0) {
      ElMessage.error(t('至少需要一个测试用例'))
      return
    }

    // 验证每个测试用例
    for (const testCase of editedParsedRequirement.value.test_cases) {
      if (!testCase.name || !testCase.objective) {
        ElMessage.error(t('测试用例名称和目标不能为空'))
        return
      }
      if (!testCase.steps || testCase.steps.length === 0) {
        ElMessage.error(t('每个测试用例至少需要一个测试步骤'))
        return
      }
    }
  } else {
    // 单个测试用例模式验证
    if (!editedParsedRequirement.value.name || !editedParsedRequirement.value.objective) {
      ElMessage.error(t('测试用例名称和目标不能为空'))
      return
    }

    // 验证步骤
    if (!editedParsedRequirement.value.steps || editedParsedRequirement.value.steps.length === 0) {
      ElMessage.error(t('至少需要一个测试步骤'))
      return
    }
  }

  // 保存编辑结果
  parsedRequirement.value = editedParsedRequirement.value
  isEditingParsed.value = false
  editedParsedRequirement.value = null

  ElMessage.success(t('解析结果已保存'))
}

const cancelEditParsedRequirement = () => {
  isEditingParsed.value = false
  editedParsedRequirement.value = null
  ElMessage.info(t('已取消编辑'))
}

const regenerateTestCase = async () => {
  if (parsedRequirement.value) {
    await generateTestCase()
  }
}

const addStep = () => {
  if (isEditingParsed.value && editedParsedRequirement.value) {
    if (!editedParsedRequirement.value.steps) {
      editedParsedRequirement.value.steps = []
    }
    editedParsedRequirement.value.steps.push({
      test_step: '',
      description: '',
      expected_result: '',
      timestamp: new Date().toISOString().slice(0, 10)
    })
  }
}

const removeStep = (index: number) => {
  if (isEditingParsed.value && editedParsedRequirement.value && editedParsedRequirement.value.steps && editedParsedRequirement.value.steps.length > 1) {
    editedParsedRequirement.value.steps.splice(index, 1)
  }
}

const exportTestCase = (format: string) => {
  if (!selectedTestCase.value) return

  switch (format) {
    case 'json':
      downloadJSON(selectedTestCase.value)
      break
    case 'markdown':
      downloadMarkdown(selectedTestCase.value)
      break
    case 'excel':
      downloadExcel(selectedTestCase.value)
      break
  }
}

const downloadJSON = (testCase: GeneratedTestCase) => {
  const filename = testCase.name.replace(/\s+/g, '_') + '.json'
  const blob = new Blob([JSON.stringify(testCase, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success(t('JSON文件下载成功'))
}

const downloadMarkdown = (testCase: GeneratedTestCase) => {
  let markdown = `# ${testCase.name}\n\n`
  markdown += `**${t('测试目标')}**: ${testCase.objective}\n\n`
  markdown += `**${t('前置条件')}**: ${testCase.preconditions}\n\n`
  markdown += `**${t('优先级')}**: ${t(testCase.priority)}\n\n`
  markdown += `## ${t('测试步骤')}\n\n`

  testCase.steps.forEach((step, index) => {
    markdown += `### ${index + 1}. ${step.test_step}\n\n`
    markdown += `${t('描述')}: ${step.description}\n\n`
    markdown += `${t('预期结果')}: ${step.expected_result}\n\n`
  })

  const filename = testCase.name.replace(/\s+/g, '_') + '.md'
  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success(t('Markdown文件下载成功'))
}

const downloadExcel = (testCase: GeneratedTestCase) => {
  // 创建工作簿
  const wb = XLSX.utils.book_new()

  // 测试用例基本信息
  const basicInfo = [
    [t('字段'), t('值')],
    [t('用例ID'), testCase.id],
    [t('用例名称'), testCase.name],
    [t('测试目标'), testCase.objective],
    [t('前置条件'), testCase.preconditions],
    [t('优先级'), t(testCase.priority)],
    [t('创建时间'), formatTime(testCase.created_at)],
    [t('步骤总数'), testCase.steps.length]
  ]

  // 创建基本信息工作表
  const wsBasic = XLSX.utils.aoa_to_sheet(basicInfo)
  // 设置列宽
  wsBasic['!cols'] = [
    { wch: 15 }, // 第一列宽度
    { wch: 50 }  // 第二列宽度
  ]
  XLSX.utils.book_append_sheet(wb, wsBasic, t('基本信息'))

  // 测试步骤数据
  const stepsData = [
    [
      t('序号'),
      t('测试步骤'),
      t('详细描述'),
      t('预期结果')
    ],
    ...testCase.steps.map((step, index) => [
      index + 1,
      step.test_step,
      step.description,
      step.expected_result
    ])
  ]

  // 创建测试步骤工作表
  const wsSteps = XLSX.utils.aoa_to_sheet(stepsData)
  // 设置列宽
  wsSteps['!cols'] = [
    { wch: 8 },  // 序号
    { wch: 25 }, // 测试步骤
    { wch: 50 }, // 详细描述
    { wch: 30 }  // 预期结果
  ]
  XLSX.utils.book_append_sheet(wb, wsSteps, t('测试步骤'))

  // 生成文件名
  const filename = testCase.name.replace(/[^\w\u4e00-\u9fa5]/g, '_') + '.xlsx'

  // 导出文件
  XLSX.writeFile(wb, filename)
  ElMessage.success(t('Excel文件下载成功'))
}

const copyTestCase = async () => {
  if (!selectedTestCase.value) return

  try {
    await navigator.clipboard.writeText(JSON.stringify(selectedTestCase.value, null, 2))
    ElMessage.success(t('测试用例已复制到剪贴板'))
  } catch (error: any) {
    console.error(t('复制失败: ') + error)
    ElMessage.error(t('复制失败'))
  }
}

const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const formatTime = (isoString: string): string => {
  return new Date(isoString).toLocaleString()
}

const handleLanguageToggle = () => {
  toggleLanguage()
  ElMessage.success(t('语言已切换'))
}

// 使用说明弹窗方法
const showUserGuide = () => {
  isUserGuideVisible.value = true
}

const closeUserGuide = () => {
  isUserGuideVisible.value = false
}

// 计算属性
const highlightedRequirementContent = computed(() => {
  if (!requirementData.description) return ''

  try {
    if (requirementLanguage.value === 'markdown') {
      return hljs.highlight(requirementData.description, { language: 'markdown' }).value
    }
    // 将纯文本换行符转换为HTML换行
    return requirementData.description.replace(/\n/g, '<br>')
  } catch (error) {
    console.warn(t('语法高亮失败: ') + error)
    return requirementData.description.replace(/\n/g, '<br>')
  }
})

const requirementStats = computed(() => {
  if (!requirementData.description) {
    return { characters: 0, lines: 0 }
  }
  return {
    characters: requirementData.description.length,
    lines: requirementData.description.split('\n').length
  }
})

// 获取不属于任何分组的单个测试用例
const singleTestCases = computed(() => {
  const groupedTestCaseIds = new Set<string>()

  testCasesGroups.value.forEach(group => {
    group.test_cases.forEach(tc => {
      groupedTestCaseIds.add(tc.id)
    })
  })

  return generatedTestCases.value.filter(tc => !groupedTestCaseIds.has(tc.id))
})

// 是否有单个测试用例
const hasSingleTestCases = computed(() => {
  return singleTestCases.value.length > 0
})

// 获取解析结果显示标题
const getDisplayTitle = computed(() => {
  const current = isEditingParsed.value ? editedParsedRequirement.value : parsedRequirement.value
  if (!current) return ''

  if (current.test_cases) {
    return ` - ${t('多测试用例解析')}`
  } else {
    return ` - ${current.name || ''}`
  }
})

// 文件上传相关方法
const beforeFileUpload = (file: any) => {
  const allowedTypes = ['text/plain', 'text/markdown', 'application/json']
  const allowedExtensions = ['.txt', '.md', '.json']

  const isValidType = allowedTypes.includes(file.type) ||
                     allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))

  if (!isValidType) {
    ElMessage.error(t('只支持 .txt, .md, .json 格式的文件'))
    return false
  }

  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    ElMessage.error(t('文件大小不能超过 5MB'))
    return false
  }

  return true
}

const handleFileUpload = (uploadFile: any) => {
  // Element Plus传递的是对象，需要获取实际的文件
  const file = uploadFile.raw || uploadFile.file

  if (!file) {
    ElMessage.error(t('文件获取失败'))
    return
  }

  if (!beforeFileUpload(file)) {
    return
  }

  isUploading.value = true

  const reader = new FileReader()
  const fileType = file.name.toLowerCase().split('.').pop()

  reader.onload = (e) => {
    try {
      const content = e.target?.result as string

      switch (fileType) {
        case 'json':
          parseJsonFile(content, file.name)
          break
        case 'md':
        case 'txt':
          parseTextFile(content, file.name)
          break
        default:
          ElMessage.error(t('不支持的文件格式'))
      }
    } catch (error: any) {
      console.error('文件解析失败:', error)
      ElMessage.error(t('文件解析失败: ') + error.message)
    } finally {
      isUploading.value = false
    }
  }

  reader.onerror = () => {
    ElMessage.error(t('文件读取失败'))
    isUploading.value = false
  }

  reader.readAsText(file, 'UTF-8')
}

const parseTextFile = (content: string, fileName: string) => {
  // 从文件名提取标题（可选）
  const titleFromFileName = fileName.replace(/\.(txt|md)$/i, '')

  // 填充需求描述
  requirementData.description = content

  // 如果标题为空，尝试从文件名设置
  if (!requirementData.title) {
    requirementData.title = titleFromFileName
  }

  ElMessage.success(t('文件加载成功: ') + fileName)
}

const parseJsonFile = (content: string, fileName: string) => {
  try {
    const data = JSON.parse(content)

    // 支持多种JSON结构
    if (data.title || data.name) {
      requirementData.title = data.title || data.name
    }

    if (data.description || data.content || data.requirement) {
      requirementData.description = data.description || data.content || data.requirement
    } else if (typeof data === 'string') {
      requirementData.description = data
    } else {
      // 如果JSON是复杂对象，尝试格式化显示
      requirementData.description = JSON.stringify(data, null, 2)
    }

    // 自动设置其他参数（如果存在）
    if (data.testType) {
      requirementData.testType = data.testType
    }

    if (data.priority) {
      requirementData.priority = data.priority
    }

    if (data.complexity) {
      requirementData.complexity = data.complexity
    }

    ElMessage.success(t('JSON文件加载成功: ') + fileName)

  } catch (error) {
    throw new Error(t('JSON格式错误: ') + error.message)
  }
}
</script>

<style scoped>
@import './RequirementGenerator.css';
</style>