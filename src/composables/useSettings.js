import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 设置管理
export function useSettings() {
  // 本地模型设置
  const useLocalModel = ref(true)
  const currentModel = ref('deepseek-r1:1.5b')
  const ollamaBaseUrl = ref('http://localhost:11434')  // 改为直接地址而不是代理路径
  const availableModels = ref([])
  
  // 远程模型设置
  const remoteModel = ref('deepseek-ai/DeepSeek-R1-0528-Qwen3-8B')
  const apiKey = ref('sk-dhyofqmlqevepadtfbjjmtvelluvgoqixawhgqcyhmiysdtl')
  
  // 通用设置
  const temperature = ref(0.7)
  const maxTokens = ref(2000)
  
  // 知识库设置
  const useKnowledgeBase = ref(true)
  const knowledgeBaseUrl = ref('/api/knowledge')
  const knowledgeBaseCollection = ref('laodongfa') // 新增：当前知识库集合
  const availableKnowledgeBases = ref([]) // 新增：可用的知识库列表
  const maxContextLength = ref(3000)
  const searchTopK = ref(5)

  // 加载设置
  function loadSettings() {
    const savedSettings = localStorage.getItem('ai-settings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      useLocalModel.value = settings.useLocalModel ?? true
      currentModel.value = settings.currentModel || 'deepseek-r1:1.5b'
      remoteModel.value = settings.remoteModel || 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'
      // 只有在 localStorage 中明确存在且非空时才覆盖默认值
      if (settings.apiKey) {
        apiKey.value = settings.apiKey
      }
      ollamaBaseUrl.value = settings.ollamaBaseUrl || 'http://localhost:11434'
      temperature.value = settings.temperature ?? 0.7
      maxTokens.value = settings.maxTokens || 1024
      useKnowledgeBase.value = settings.useKnowledgeBase ?? true
      knowledgeBaseUrl.value = settings.knowledgeBaseUrl || '/api/knowledge'
      knowledgeBaseCollection.value = settings.knowledgeBaseCollection || 'laodongfa' // 加载知识库选择
      maxContextLength.value = settings.maxContextLength || 3000
      searchTopK.value = settings.searchTopK || 5
    }
  }

  // 加载 Ollama 模型列表
  async function loadOllamaModels() {
    try {
      const response = await fetch(`${ollamaBaseUrl.value}/api/tags`)
      if (response.ok) {
        const data = await response.json()
        availableModels.value = data.models || []
        ElMessage.success(`连接成功！找到 ${availableModels.value.length} 个本地模型`)
        return true
      } else {
        throw new Error('连接失败')
      }
    } catch (error) {
      ElMessage.error(`无法连接到 Ollama: ${error.message}`)
      return false
    }
  }

  // 新增：加载知识库列表
  async function loadKnowledgeBases() {
    if (!knowledgeBaseUrl.value) {
      console.error('知识库 API 地址未设置。')
      return
    }
    try {
      // 修正：直接构建完整的后端 URL，绕过 Vite 代理进行测试
      // 后端 API 默认运行在 8000 端口
      const baseUrl = 'http://127.0.0.1:8000';
      const response = await fetch(`${baseUrl}/collections`);

      if (!response.ok) {
        throw new Error(`获取知识库列表失败: ${response.statusText}`)
      }
      const data = await response.json()
      // 后端返回的是对象数组，我们需要提取 name 字段
      availableKnowledgeBases.value = data.map(c => c.name)
      
      // 如果当前选中的知识库不存在于新列表中，则默认选中第一个
      if (availableKnowledgeBases.value.length > 0 && !availableKnowledgeBases.value.includes(knowledgeBaseCollection.value)) {
        knowledgeBaseCollection.value = availableKnowledgeBases.value[0]
      }
    } catch (error) {
      console.error('加载知识库列表时出错:', error)
      availableKnowledgeBases.value = [] // 出错时清空列表
    }
  }

  // 保存设置
  function saveSettings() {
    const settings = {
      useLocalModel: useLocalModel.value,
      currentModel: currentModel.value,
      remoteModel: remoteModel.value,
      apiKey: apiKey.value,
      ollamaBaseUrl: ollamaBaseUrl.value,
      temperature: temperature.value,
      maxTokens: maxTokens.value,
      useKnowledgeBase: useKnowledgeBase.value,
      knowledgeBaseUrl: knowledgeBaseUrl.value,
      knowledgeBaseCollection: knowledgeBaseCollection.value, // 保存知识库选择
      maxContextLength: maxContextLength.value,
      searchTopK: searchTopK.value
    }
    localStorage.setItem('ai-settings', JSON.stringify(settings))
    ElMessage.success('设置已保存')
  }

  return {
    useLocalModel,
    currentModel,
    ollamaBaseUrl,
    availableModels,
    remoteModel,
    apiKey,
    temperature,
    maxTokens,
    useKnowledgeBase,
    knowledgeBaseUrl,
    knowledgeBaseCollection,
    availableKnowledgeBases,
    maxContextLength,
    searchTopK,
    loadSettings,
    saveSettings,
    loadOllamaModels,
    loadKnowledgeBases
  }
}
