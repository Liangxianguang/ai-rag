<template>
  <div class="chat-container">
    <!-- 头部标题 -->
    <header class="chat-header">
      <div class="header-left">
        <div class="logo">🤖</div>
        <div class="title-info">
          <h1>AI 智能助手</h1>
          <div class="subtitle">基于知识库的智能问答系统</div>
        </div>
      </div>
      <div class="header-actions">
        <el-tooltip content="清空对话">
          <el-button
            type="text"
            :icon="Delete"
            @click="clearChat"
            class="header-btn"
          />
        </el-tooltip>
        <el-tooltip content="设置">
          <el-button
            type="text"
            :icon="Setting"
            @click="showSettings = true"
            class="header-btn"
          />
        </el-tooltip>
      </div>
    </header>

    <!-- 聊天区域 -->
    <main class="chat-main">
      <!-- 侧边栏 -->
      <ChatSidebar
        :sessions="chatSessions"
        :current-index="currentSessionIndex"
        @new-chat="newChat"
        @switch-session="switchSession"
        @delete-session="deleteSession"
      />

      <!-- 消息区域 -->
      <div class="chat-content">
        <ChatMessages
          ref="messagesRef"
          :messages="currentSession.messages"
          :loading="loading"
          @copy-text="copyText"
          @like-message="likeMessage"
          @regenerate-response="regenerateResponse"
        />

        <!-- 输入区域 -->
        <ChatInput
          v-model:msg="msg"
          :loading="loading"
          @send-msg="handleSendMsg"
          @file-processed="handleFileProcessed"
        />
      </div>
    </main>

    <!-- 设置对话框 -->
    <SettingsDialog
      v-model:show-settings="showSettings"
      :settings="settingsData"
      @save-settings="handleSaveSettings"
      @load-models="loadOllamaModels"
      @load-knowledge-bases="loadKnowledgeBases" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Delete, Setting } from '@element-plus/icons-vue'

// 组件导入
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatInput from '@/components/ChatInput.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'

// Composables 导入
import { useChat } from '@/composables/useChat'
import { useSettings } from '@/composables/useSettings'
import { useMessageSender } from '@/composables/useMessageSender'
import { useTextUtils } from '@/utils/helpers'

// 响应式数据
const msg = ref('')
const showSettings = ref(false)
const messagesRef = ref(null)

// 使用 composables
const chatComposable = useChat()
const {
  chatSessions,
  currentSessionIndex,
  currentSession,
  loading,
  newChat,
  switchSession,
  deleteSession,
  clearChat,
  scrollToBottom,
  initSessions,
  saveSessions
} = chatComposable

const settingsComposable = useSettings()
const {
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
  knowledgeBaseCollection, // 新增
  availableKnowledgeBases, // 新增
  maxContextLength,
  searchTopK,
  loadSettings,
  saveSettings,
  loadOllamaModels,
  loadKnowledgeBases // 新增
} = settingsComposable

// 设置数据对象
const settingsData = computed(() => ({
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
  knowledgeBaseCollection, // 新增
  availableKnowledgeBases, // 新增
  maxContextLength,
  searchTopK
}))

const messageSender = useMessageSender(chatComposable, settingsData) //不再使用 .value，传递整个 computed ref
const { sendMsg, sendQuickMessage } = messageSender

const { copyText, likeMessage, regenerateResponse } = useTextUtils()

// 初始化
onMounted(async () => {
  // 加载会话和设置
  initSessions()
  loadSettings()

  // 如果使用本地模型，尝试加载模型列表
  if (useLocalModel.value) {
    await loadOllamaModels()
  }
  // 如果启用知识库，则加载知识库列表
  if (useKnowledgeBase.value) {
    await loadKnowledgeBases()
  }
})

// 处理发送消息
function handleSendMsg() {
  if (!msg.value.trim()) return
  
  const message = msg.value
  msg.value = ''
  sendMsg(message)
}

// 处理文件处理完成
function handleFileProcessed(fileMessage) {
  if (fileMessage) {
    currentSession.value.messages.push(fileMessage)
    scrollToBottom()
  }
}

// 处理保存设置 - 正确更新所有原始 ref
function handleSaveSettings(newSettings) {
  // newSettings 是从子组件 emit 出来的普通对象，不包含 .value
  useLocalModel.value = newSettings.useLocalModel
  currentModel.value = newSettings.currentModel
  remoteModel.value = newSettings.remoteModel
  apiKey.value = newSettings.apiKey
  ollamaBaseUrl.value = newSettings.ollamaBaseUrl
  temperature.value = newSettings.temperature
  maxTokens.value = newSettings.maxTokens
  useKnowledgeBase.value = newSettings.useKnowledgeBase
  knowledgeBaseUrl.value = newSettings.knowledgeBaseUrl
  knowledgeBaseCollection.value = newSettings.knowledgeBaseCollection // 新增
  maxContextLength.value = newSettings.maxContextLength
  searchTopK.value = newSettings.searchTopK

  // 调用 useSettings 中的保存函数，将更新后的值存入 localStorage
  saveSettings()
}

// 监听会话变化，自动保存
watch(chatSessions, saveSessions, { deep: true })

// 监听消息容器变化，自动滚动
watch(() => messagesRef.value?.messagesContainer, (container) => {
  if (container) {
    chatComposable.messagesContainer.value = container
  }
}, { immediate: true })
</script>

<style scoped>
/* 更现代的渐变背景，色彩更明亮，整体更大气 */
/* 更现代的蓝紫渐变背景，去除粉色，视觉更清爽 */
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(120deg, #6a85b6 0%, #bac8e0 100%);
  position: relative;
  overflow: hidden;
}

.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.12) 0%, transparent 60%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.08) 0%, transparent 60%),
    radial-gradient(circle at 40% 70%, rgba(255, 255, 255, 0.06) 0%, transparent 60%);
  pointer-events: none;
  z-index: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 56px;
  height: 100px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(24px) saturate(200%);
  border-bottom: 1.5px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.10);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 38px;
  box-shadow: 0 12px 32px rgba(161, 140, 209, 0.25);
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.08);
}

.title-info h1 {
  margin: 0;
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 20px;
  color: #7b6f99;
  font-weight: 600;
  margin-top: 6px;
}

.header-actions {
  display: flex;
  gap: 24px;
}

.header-btn {
  border-radius: 18px;
  padding: 18px;
  font-size: 26px;
  transition: all 0.3s ease;
}

.header-btn:hover {
  transform: translateY(-3px) scale(1.08);
  box-shadow: 0 12px 32px rgba(161, 140, 209, 0.18);
}

/* 主体区域更大，底部输入区紧贴底部 */
.chat-main {
  flex: 1;
  display: flex;
  min-height: 0;
  position: relative;
  z-index: 1;
  padding: 0 32px 24px 32px;
  gap: 32px;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.13);
  backdrop-filter: blur(24px) saturate(180%);
  min-height: 0;
  border-radius: 32px;
  box-shadow: 0 8px 32px rgba(106, 133, 182, 0.10);
  padding: 32px 32px 0 32px;
  box-sizing: border-box;
  overflow: hidden;
  font-size: 22px;
  justify-content: flex-end;
}
</style>
