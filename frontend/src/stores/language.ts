import { ref } from 'vue'
import { defineStore } from 'pinia'

export type Language = 'zh' | 'en'

export interface Translation {
  zh: string
  en: string
}

export const useLanguageStore = defineStore('language', () => {
  const currentLanguage = ref<Language>('zh')

  const translations = ref<Record<string, Translation>>({
    // 标题和导航
    '需求生成测试用例系统': { zh: '需求生成测试用例系统', en: 'Requirement to Test Case Generator' },
    '会话ID': { zh: '会话ID', en: 'Session ID' },

    // 侧边栏
    '需求输入': { zh: '需求输入', en: 'Requirement Input' },
    '需求模板': { zh: '需求模板', en: 'Requirement Template' },
    '选择需求模板': { zh: '选择需求模板', en: 'Select Requirement Template' },
    '需求标题': { zh: '需求标题', en: 'Requirement Title' },
    '需求描述': { zh: '需求描述', en: 'Requirement Description' },
    '请输入需求标题': { zh: '请输入需求标题', en: 'Please enter requirement title' },
    '测试类型': { zh: '测试类型', en: 'Test Type' },
    '选择测试类型': { zh: '选择测试类型', en: 'Select Test Type' },
    '优先级': { zh: '优先级', en: 'Priority' },
    '选择优先级': { zh: '选择优先级', en: 'Select Priority' },
    '预估复杂度': { zh: '预估复杂度', en: 'Estimated Complexity' },
    '选择复杂度': { zh: '选择复杂度', en: 'Select Complexity' },
    '解析需求': { zh: '解析需求', en: 'Parse Requirement' },
    '生成测试用例': { zh: '生成测试用例', en: 'Generate Test Case' },
    '重置': { zh: '重置', en: 'Reset' },

    // 测试类型选项
    '功能测试': { zh: '功能测试', en: 'Functional Testing' },
    '性能测试': { zh: '性能测试', en: 'Performance Testing' },
    '安全测试': { zh: '安全测试', en: 'Security Testing' },
    '兼容性测试': { zh: '兼容性测试', en: 'Compatibility Testing' },
    '用户体验测试': { zh: '用户体验测试', en: 'User Experience Testing' },

    // 优先级选项
    '高': { zh: '高', en: 'High' },
    '中': { zh: '中', en: 'Medium' },
    '低': { zh: '低', en: 'Low' },

    // 复杂度选项
    '简单': { zh: '简单', en: 'Simple' },
    '中等': { zh: '中等', en: 'Medium' },
    '复杂': { zh: '复杂', en: 'Complex' },
    '简单复杂度': { zh: '简单复杂度', en: 'Simple Complexity' },
    '中等复杂度': { zh: '中等复杂度', en: 'Medium Complexity' },
    '复杂复杂度': { zh: '复杂复杂度', en: 'Complex Complexity' },
    '复杂度说明': { zh: '复杂度说明', en: 'Complexity Description' },
    '生成单个测试用例，包含3-4个核心测试步骤，覆盖主要功能点': {
      zh: '生成单个测试用例，包含3-4个核心测试步骤，覆盖主要功能点',
      en: 'Generate a single test case with 3-4 core test steps covering main functionalities'
    },
    '生成单个测试用例，包含5-6个测试步骤，包含正常流程和基本异常场景': {
      zh: '生成单个测试用例，包含5-6个测试步骤，包含正常流程和基本异常场景',
      en: 'Generate a single test case with 5-6 test steps including normal flow and basic exception scenarios'
    },
    '生成2-4个相关测试用例，分别关注基本功能验证、异常场景处理、边界条件测试等': {
      zh: '生成2-4个相关测试用例，分别关注基本功能验证、异常场景处理、边界条件测试等',
      en: 'Generate 2-4 related test cases focusing on basic function validation, exception handling, boundary condition testing'
    },
    '单个测试用例，3-4步': { zh: '单个测试用例，3-4步', en: 'Single test case, 3-4 steps' },
    '单个测试用例，5-6步': { zh: '单个测试用例，5-6步', en: 'Single test case, 5-6 steps' },
    '多个测试用例，分组覆盖': { zh: '多个测试用例，分组覆盖', en: 'Multiple test cases, group coverage' },
    '成功生成': { zh: '成功生成', en: 'Successfully generated' },

    // 生成的测试用例
    '生成的测试用例': { zh: '生成的测试用例', en: 'Generated Test Cases' },
    '个步骤': { zh: '个步骤', en: ' steps' },
    '个': { zh: '个', en: '' },
    '需求组': { zh: '需求组', en: 'Requirement Group' },
    '个测试用例': { zh: '个测试用例', en: ' test cases' },
    '其他测试用例': { zh: '其他测试用例', en: 'Other Test Cases' },
    '多测试用例解析': { zh: '多测试用例解析', en: 'Multiple Test Cases Parsed' },
    '覆盖说明': { zh: '覆盖说明', en: 'Coverage Description' },
    '预览测试用例': { zh: '预览测试用例', en: 'Test Cases Preview' },

    // 文件上传相关
    '加载文件': { zh: '加载文件', en: 'Load File' },
    '支持 .txt, .md, .json 格式': { zh: '支持 .txt, .md, .json 格式', en: 'Supports .txt, .md, .json formats' },
    '支持 .txt, .md, .json 格式，最大5MB': { zh: '支持 .txt, .md, .json 格式，最大5MB', en: 'Supports .txt, .md, .json formats, max 5MB' },
    '从文件加载需求': { zh: '从文件加载需求', en: 'Load Requirements from File' },
    '点击或拖拽文件到此区域上传': { zh: '点击或拖拽文件到此区域上传', en: 'Click or drag file to this area to upload' },
    '只支持 .txt, .md, .json 格式的文件': { zh: '只支持 .txt, .md, .json 格式的文件', en: 'Only .txt, .md, .json files are supported' },
    '文件大小不能超过 5MB': { zh: '文件大小不能超过 5MB', en: 'File size cannot exceed 5MB' },
    '文件加载成功': { zh: '文件加载成功', en: 'File loaded successfully' },
    'JSON文件加载成功': { zh: 'JSON文件加载成功', en: 'JSON file loaded successfully' },
    '不支持的文件格式': { zh: '不支持的文件格式', en: 'Unsupported file format' },
    '文件解析失败': { zh: '文件解析失败', en: 'File parsing failed' },
    '文件读取失败': { zh: '文件读取失败', en: 'File read failed' },
    '文件获取失败': { zh: '文件获取失败', en: 'Failed to get file' },
    'JSON格式错误': { zh: 'JSON格式错误', en: 'JSON format error' },

    // 解析结果
    '解析结果': { zh: '解析结果', en: 'Parse Result' },
    '编辑': { zh: '编辑', en: 'Edit' },
    '编辑解析结果': { zh: '编辑解析结果', en: 'Edit Parse Result' },
    '保存': { zh: '保存', en: 'Save' },
    '取消': { zh: '取消', en: 'Cancel' },
    '请输入覆盖说明': { zh: '请输入覆盖说明', en: 'Please enter coverage description' },
    '覆盖方面': { zh: '覆盖方面', en: 'Coverage Aspect' },
    '测试用例名称和目标不能为空': { zh: '测试用例名称和目标不能为空', en: 'Test case name and objective cannot be empty' },
    '至少需要一个测试步骤': { zh: '至少需要一个测试步骤', en: 'At least one test step is required' },
    '解析结果已保存': { zh: '解析结果已保存', en: 'Parse result saved' },
    '已取消编辑': { zh: '已取消编辑', en: 'Edit cancelled' },
    '没有可编辑的解析结果': { zh: '没有可编辑的解析结果', en: 'No editable parse result' },
    '没有可保存的修改': { zh: '没有可保存的修改', en: 'No modifications to save' },
    '重新生成': { zh: '重新生成', en: 'Regenerate' },
    '测试用例名称': { zh: '测试用例名称', en: 'Test Case Name' },
    '测试目标': { zh: '测试目标', en: 'Test Objective' },
    '前置条件': { zh: '前置条件', en: 'Preconditions' },
    '测试步骤': { zh: '测试步骤', en: 'Test Steps' },
    '添加步骤': { zh: '添加步骤', en: 'Add Step' },

    // 测试用例详情
    '测试用例详情': { zh: '测试用例详情', en: 'Test Case Details' },
    '导出JSON': { zh: '导出JSON', en: 'Export JSON' },
    '导出Markdown': { zh: '导出Markdown', en: 'Export Markdown' },
    '导出Excel': { zh: '导出Excel', en: 'Export Excel' },
    '复制': { zh: '复制', en: 'Copy' },

    // 表格列名
    '用例ID': { zh: '用例ID', en: 'Case ID' },
    '用例名称': { zh: '用例名称', en: 'Case Name' },
    '详细描述': { zh: '详细描述', en: 'Description' },
    '预期结果': { zh: '预期结果', en: 'Expected Result' },
    '创建时间': { zh: '创建时间', en: 'Created Time' },

    // 状态信息
    '正在解析需求...': { zh: '正在解析需求...', en: 'Parsing requirement...' },
    '正在生成测试用例...': { zh: '正在生成测试用例...', en: 'Generating test case...' },
    '服务连接失败': { zh: '服务连接失败', en: 'Service connection failed' },

    // 需求模板
    '雨刷器功能测试': { zh: '雨刷器功能测试', en: 'Wiper Function Test' },
    '验证车辆雨刷器各项功能的正常工作': { zh: '验证车辆雨刷器各项功能的正常工作', en: 'Verify proper functioning of vehicle wiper features' },
    '雨刷器功能测试需求': { zh: '雨刷器功能测试需求', en: 'Wiper Function Test Requirements' },
    '模板测试目标': { zh: '测试目标', en: 'Test Objectives' },
    '功能要求': { zh: '功能要求', en: 'Functional Requirements' },
    '测试条件': { zh: '测试条件', en: 'Test Conditions' },

    'CAN通信测试': { zh: 'CAN通信测试', en: 'CAN Communication Test' },
    '验证CAN总线通信的正确性和稳定性': { zh: '验证CAN总线通信的正确性和稳定性', en: 'Verify correctness and stability of CAN bus communication' },
    'CAN通信测试需求': { zh: 'CAN通信测试需求', en: 'CAN Communication Test Requirements' },
    '通信要求': { zh: '通信要求', en: 'Communication Requirements' },

    '系统性能测试': { zh: '系统性能测试', en: 'System Performance Test' },
    '验证系统在不同负载下的性能表现': { zh: '验证系统在不同负载下的性能表现', en: 'Verify system performance under different loads' },
    '系统性能测试需求': { zh: '系统性能测试需求', en: 'System Performance Test Requirements' },
    '性能要求': { zh: '性能要求', en: 'Performance Requirements' },

    // 通用词汇
    '纯文本': { zh: '纯文本', en: 'Plain Text' },
    '字符': { zh: '字符', en: 'characters' },
    '行': { zh: '行', en: 'lines' },
    '描述': { zh: '描述', en: 'Description' },
    '应用模板': { zh: '应用模板', en: 'Apply Template' },
    '已应用模板: ': { zh: '已应用模板: ', en: 'Template applied: ' },
    '请填写需求标题和描述': { zh: '请填写需求标题和描述', en: 'Please fill in requirement title and description' },
    '需求解析完成，共提取 ': { zh: '需求解析完成，共提取 ', en: 'Requirement parsing completed, extracted ' },
    '个测试步骤': { zh: '个测试步骤', en: ' test steps' },
    '请先解析需求': { zh: '请先解析需求', en: 'Please parse requirement first' },
    '测试用例生成完成: ': { zh: '测试用例生成完成: ', en: 'Test case generation completed: ' },
    '表单已重置': { zh: '表单已重置', en: 'Form has been reset' },
    '编辑功能开发中': { zh: '编辑功能开发中', en: 'Edit feature under development' },
    'Excel导出功能开发中': { zh: 'Excel导出功能开发中', en: 'Excel export feature under development' },
    'JSON文件下载成功': { zh: 'JSON文件下载成功', en: 'JSON file downloaded successfully' },
    'Markdown文件下载成功': { zh: 'Markdown文件下载成功', en: 'Markdown file downloaded successfully' },
    '测试用例已复制到剪贴板': { zh: '测试用例已复制到剪贴板', en: 'Test case copied to clipboard' },
    '复制失败': { zh: '复制失败', en: 'Copy failed' },
    '语言已切换': { zh: '语言已切换', en: 'Language switched' },
    '语法高亮失败: ': { zh: '语法高亮失败: ', en: 'Syntax highlighting failed: ' },

    // 语言切换
    'Switch to English': { zh: 'Switch to English', en: 'Switch to English' },
    '切换到中文': { zh: '切换到中文', en: 'Switch to Chinese' },

    // LLM服务相关错误
    '未配置OPENAI_API_KEY环境变量，请在.env文件中设置API密钥': {
      zh: '未配置OPENAI_API_KEY环境变量，请在.env文件中设置API密钥',
      en: 'OPENAI_API_KEY environment variable not configured, please set API key in .env file'
    },
    '无法连接到OpenAI服务': {
      zh: '无法连接到OpenAI服务，请检查网络连接和API配置',
      en: 'Cannot connect to OpenAI service, please check network connection and API configuration'
    },
    'OpenAI API密钥无效或已过期': {
      zh: 'OpenAI API密钥无效或已过期，请检查API密钥配置',
      en: 'OpenAI API key is invalid or expired, please check API key configuration'
    },
    'OpenAI API调用频率超限': {
      zh: 'OpenAI API调用频率超限，请稍后重试',
      en: 'OpenAI API rate limit exceeded, please try again later'
    },
    'OpenAI API错误': {
      zh: 'OpenAI API调用失败，请检查服务状态',
      en: 'OpenAI API call failed, please check service status'
    },
    'LLM解析失败': {
      zh: 'LLM服务解析失败，请检查LLM服务配置',
      en: 'LLM service parsing failed, please check LLM service configuration'
    },
    'LLM返回的不是有效的JSON格式': {
      zh: 'LLM返回的格式不正确，请重试',
      en: 'LLM returned invalid format, please try again'
    },
    'LLM返回结果缺少必需字段': {
      zh: 'LLM返回的结果不完整，请重试',
      en: 'LLM returned incomplete result, please try again'
    },
    'LLM返回的steps字段为空或格式错误': {
      zh: 'LLM未返回有效的测试步骤，请重试',
      en: 'LLM did not return valid test steps, please try again'
    }
  })

  function t(key: string): string {
    const translation = translations.value[key]
    if (!translation) return key
    return translation[currentLanguage.value] || key
  }

  function toggleLanguage(): void {
    currentLanguage.value = currentLanguage.value === 'zh' ? 'en' : 'zh'
    localStorage.setItem('requirement_language', currentLanguage.value)
  }

  function setLanguage(lang: Language): void {
    currentLanguage.value = lang
    localStorage.setItem('requirement_language', lang)
  }

  function initLanguage(): void {
    const saved = localStorage.getItem('requirement_language') as Language | null
    if (saved && (saved === 'zh' || saved === 'en')) {
      currentLanguage.value = saved
    }
  }

  return {
    currentLanguage,
    t,
    toggleLanguage,
    setLanguage,
    initLanguage
  }
})