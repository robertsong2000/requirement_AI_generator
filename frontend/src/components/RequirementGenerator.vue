<template>
  <div class="container">
    <!-- 头部 -->
    <header class="header">
      <h1>{{ t('需求生成测试用例系统') }}</h1>
      <div class="header-actions">
        <el-button
          @click="handleLanguageToggle"
          size="small"
          type="primary"
          circle
          :title="languageStore.currentLanguage === 'zh' ? t('Switch to English') : t('切换到中文')"
        >
          {{ languageStore.currentLanguage === 'zh' ? 'EN' : '中' }}
        </el-button>
        <div class="session-info">
          {{ t('会话ID') }}: {{ sessionId }}
          <span :class="['status-indicator', isConnected ? 'status-connected' : 'status-disconnected']"></span>
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

          <!-- 需求描述输入 -->
          <el-form-item :label="t('需求描述')">
            <el-input
              v-model="requirementData.description"
              type="textarea"
              :rows="8"
              :placeholder="t('请输入详细的需求描述...')"
              maxlength="5000"
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
              <el-select v-model="requirementData.complexity" :placeholder="t('选择复杂度')">
                <el-option :label="t('简单')" value="simple" />
                <el-option :label="t('中等')" value="medium" />
                <el-option :label="t('复杂')" value="complex" />
              </el-select>
            </el-form-item>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button type="primary" @click="parseRequirement" :loading="isParsing">
              🔍 {{ t('解析需求') }}
            </el-button>
            <el-button type="success" @click="generateTestCase" :loading="isGenerating" :disabled="!parsedRequirement">
              🚀 {{ t('生成测试用例') }}
            </el-button>
            <el-button @click="resetForm">
              🔄 {{ t('重置') }}
            </el-button>
          </div>
        </section>

        <!-- 生成的测试用例列表 -->
        <section class="testcase-list-panel" v-if="generatedTestCases.length > 0">
          <h3>📋 {{ t('生成的测试用例') }}</h3>
          <div class="testcase-list">
            <el-card
              v-for="(testCase, index) in generatedTestCases"
              :key="testCase.id"
              :class="['testcase-item', { selected: selectedTestCase?.id === testCase.id }]"
              @click="selectTestCase(testCase)"
              shadow="hover"
            >
              <div class="testcase-header">
                <strong>{{ testCase.name }}</strong>
                <el-tag :type="getPriorityType(testCase.priority)" size="small">
                  {{ t(testCase.priority) }}
                </el-tag>
              </div>
              <p class="testcase-description">{{ testCase.objective }}</p>
              <div class="testcase-meta">
                <span class="testcase-steps">{{ testCase.steps?.length || 0 }} {{ t('个步骤') }}</span>
                <span class="testcase-time">{{ formatTime(testCase.created_at) }}</span>
              </div>
            </el-card>
          </div>
        </section>
      </aside>

      <!-- 右侧内容区域 -->
      <main class="content-area">
        <!-- 需求描述面板 -->
        <section class="requirement-description-panel" v-if="requirementData.description">
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
            </div>
          </div>

          <div class="requirement-display">
            <div
              class="requirement-content-display"
              :class="{
                'language-markdown': requirementLanguage === 'markdown',
                'language-plaintext': requirementLanguage === 'plaintext'
              }"
              v-html="highlightedRequirementContent"
            ></div>
          </div>
        </section>

        <!-- 解析结果面板 -->
        <section class="parse-result-panel" v-if="parsedRequirement">
          <div class="panel-header">
            <h3>🔍 {{ t('解析结果') }}
              <span v-if="parsedRequirement" style="color: #409eff; font-size: 14px; font-weight: normal;">
                - {{ parsedRequirement.name }}
              </span>
            </h3>
            <div class="panel-actions">
              <el-button size="small" @click="editParsedRequirement">
                ✏️ {{ t('编辑') }}
              </el-button>
              <el-button size="small" type="success" @click="regenerateTestCase">
                🔄 {{ t('重新生成') }}
              </el-button>
            </div>
          </div>

          <div class="parsed-content">
            <el-form :model="parsedRequirement" label-width="120px">
              <el-form-item :label="t('测试用例名称')">
                <el-input v-model="parsedRequirement.name" />
              </el-form-item>
              <el-form-item :label="t('测试目标')">
                <el-input v-model="parsedRequirement.objective" type="textarea" :rows="2" />
              </el-form-item>
              <el-form-item :label="t('前置条件')">
                <el-input v-model="parsedRequirement.preconditions" type="textarea" :rows="2" />
              </el-form-item>
            </el-form>

            <!-- 测试步骤 -->
            <div class="steps-section">
              <h4>{{ t('测试步骤') }}</h4>
              <div class="steps-list">
                <div
                  v-for="(step, index) in parsedRequirement.steps"
                  :key="index"
                  class="step-item"
                >
                  <div class="step-header">
                    <span class="step-number">{{ index + 1 }}</span>
                    <el-button size="small" type="danger" @click="removeStep(index)">
                      🗑️
                    </el-button>
                  </div>
                  <el-input
                    v-model="step.test_step"
                    :placeholder="t('测试步骤')"
                    class="step-input"
                  />
                  <el-input
                    v-model="step.description"
                    :placeholder="t('详细描述')"
                    type="textarea"
                    :rows="2"
                    class="step-description"
                  />
                  <el-input
                    v-model="step.expected_result"
                    :placeholder="t('预期结果')"
                    class="step-expected"
                  />
                </div>
                <el-button @click="addStep" type="primary" plain>
                  ➕ {{ t('添加步骤') }}
                </el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import 'element-plus/dist/index.css'
import 'highlight.js/styles/github.css'
import hljs from 'highlight.js/lib/core'
import markdown from 'highlight.js/lib/languages/markdown'
import { useLanguageStore } from '../stores/language'

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
}

interface ParsedRequirement {
  id: string
  name: string
  objective: string
  preconditions: string
  steps: Array<{
    test_step: string
    description: string
    expected_result: string
    timestamp: string
  }>
}

interface GeneratedTestCase {
  id: string
  name: string
  objective: string
  preconditions: string
  priority: string
  steps: Array<{
    test_step: string
    description: string
    expected_result: string
    timestamp: string
  }>
  created_at: string
}

// 响应式数据
const sessionId = ref<string>(localStorage.getItem('requirement_session_id') || 'session_' + Math.random().toString(36).substr(2, 9))
const isConnected = ref<boolean>(false)
const selectedTemplate = ref<string>('')
const requirementLanguage = ref<'markdown' | 'plaintext'>('markdown')
const isParsing = ref<boolean>(false)
const isGenerating = ref<boolean>(false)
const errorMessage = ref<string>('')
const parsedRequirement = ref<ParsedRequirement | null>(null)
const selectedTestCase = ref<GeneratedTestCase | null>(null)
const generatedTestCases = ref<GeneratedTestCase[]>([])

// 表单数据
const requirementData = reactive<RequirementData>({
  title: '',
  description: '',
  testType: 'functional',
  priority: 'medium',
  complexity: 'medium'
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
    await axios.get(`${API_BASE_URL}/health`)
    isConnected.value = true
  } catch (_: any) {
    isConnected.value = false
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
      session_id: sessionId.value
    })

    if (response.data.error) {
      errorMessage.value = response.data.error
      ElMessage.error(t('需求解析失败: ') + response.data.error)
      return
    }

    parsedRequirement.value = response.data.parsed_requirement
    ElMessage.success(t('需求解析完成，共提取 ') + parsedRequirement.value.steps.length + t('个测试步骤'))

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
      session_id: sessionId.value
    })

    if (response.data.error) {
      errorMessage.value = response.data.error
      ElMessage.error(t('测试用例生成失败: ') + response.data.error)
      return
    }

    const newTestCase: GeneratedTestCase = {
      ...response.data.test_case,
      created_at: new Date().toISOString()
    }

    generatedTestCases.value.push(newTestCase)
    selectedTestCase.value = newTestCase
    ElMessage.success(t('测试用例生成完成: ') + newTestCase.name)

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

const resetForm = () => {
  requirementData.title = ''
  requirementData.description = ''
  requirementData.testType = 'functional'
  requirementData.priority = 'medium'
  requirementData.complexity = 'medium'
  selectedTemplate.value = ''
  parsedRequirement.value = null
  selectedTestCase.value = null
  errorMessage.value = ''
  ElMessage.success(t('表单已重置'))
}

const editParsedRequirement = () => {
  ElMessage.info(t('编辑功能开发中'))
}

const regenerateTestCase = async () => {
  if (parsedRequirement.value) {
    await generateTestCase()
  }
}

const addStep = () => {
  if (parsedRequirement.value) {
    parsedRequirement.value.steps.push({
      test_step: '',
      description: '',
      expected_result: '',
      timestamp: new Date().toISOString().slice(0, 10)
    })
  }
}

const removeStep = (index: number) => {
  if (parsedRequirement.value && parsedRequirement.value.steps.length > 1) {
    parsedRequirement.value.steps.splice(index, 1)
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
      ElMessage.info(t('Excel导出功能开发中'))
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
</script>

<style scoped>
@import './RequirementGenerator.css';
</style>