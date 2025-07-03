<template>
  <footer class="chat-input">
    <div class="input-wrapper">
      <div class="input-box">
        <el-input
          v-model="localMsg"
          @input="handleInput"
          @keydown.enter.exact.prevent="$emit('sendMsg')"
          @keydown.enter.shift.exact="handleShiftEnter"
          :disabled="loading"
          placeholder="输入您的问题... (Enter发送，Shift+Enter换行)"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          class="message-input"
          resize="none"
        />
        <div class="input-tools">
          <el-tooltip content="表情">
            <el-button
              type="text"
              :icon="ChatDotRound"
              @click="showEmojiPicker = !showEmojiPicker"
              class="tool-btn"
            />
          </el-tooltip>
          <el-tooltip content="上传文件">
            <el-button
              type="text"
              :icon="Promotion"
              @click="handleFileUpload"
              class="tool-btn"
            />
          </el-tooltip>
          <el-button
            type="primary"
            :icon="ChatRound"
            @click="$emit('sendMsg')"
            :loading="loading"
            class="send-btn"
            :disabled="!localMsg.trim()"
          >
            发送
          </el-button>
        </div>
      </div>

      <!-- 表情选择器 -->
      <div v-if="showEmojiPicker" class="emoji-picker">
        <div class="emoji-header">
          <span>选择表情</span>
          <el-button
            type="text"
            :icon="Close"
            @click="showEmojiPicker = false"
            size="small"
          />
        </div>
        <div class="emoji-grid">
          <div 
            v-for="emoji in commonEmojis" 
            :key="emoji" 
            class="emoji-item" 
            @click="insertEmoji(emoji)"
          >
            {{ emoji }}
          </div>
        </div>
      </div>

      <!-- 隐藏的文件输入 -->
      <input 
        ref="fileInputRef" 
        type="file" 
        style="display: none" 
        @change="onFileSelected"
        accept="image/*,text/*,.pdf,.doc,.docx"
      />
    </div>
  </footer>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { 
  ChatRound, ChatDotRound, Promotion, Close 
} from '@element-plus/icons-vue'
import { useEmoji, useFileHandler } from '@/utils/helpers'

const props = defineProps({
  msg: {
    type: String,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:msg', 'sendMsg', 'fileProcessed'])

// 本地消息状态
const localMsg = ref(props.msg)

// 使用工具函数
const { showEmojiPicker, commonEmojis, insertEmoji: _insertEmoji } = useEmoji()
const { fileInputRef, handleFileUpload, onFileSelected: _onFileSelected } = useFileHandler()

// 监听 props 变化
watch(() => props.msg, (newVal) => {
  localMsg.value = newVal
})

// 监听本地变化并同步到父组件
watch(localMsg, (newVal) => {
  emit('update:msg', newVal)
})

// 处理输入
function handleInput() {
  nextTick(() => {
    const textarea = document.querySelector('.message-input textarea')
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  })
}

// 处理 Shift+Enter
function handleShiftEnter(event) {
  // 不阻止默认行为，允许换行
}

// 插入表情
function insertEmoji(emoji) {
  _insertEmoji(emoji, localMsg)
}

// 文件选择处理
function onFileSelected(event) {
  _onFileSelected(event, (fileMessage, fileContent) => {
    if (fileMessage) {
      emit('fileProcessed', fileMessage)
    }
    if (fileContent) {
      localMsg.value += fileContent
    }
  })
}
</script>

<style scoped>
/* 输入区紧贴底部，整体更大，按钮和表情更大更易点 */
.chat-input {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(24px) saturate(180%);
  border-top: 1.5px solid rgba(106, 133, 182, 0.18);
  padding: 32px 48px 32px 48px;
  position: relative;
  z-index: 10;
  width: 100%;
  box-sizing: border-box;
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-sizing: border-box;
}

.input-box {
  display: flex;
  align-items: flex-end;
  gap: 32px;
  background: white;
  border-radius: 28px;
  padding: 24px 32px;
  box-shadow: 0 8px 32px rgba(106, 133, 182, 0.10);
  border: 1.5px solid rgba(106, 133, 182, 0.08);
  transition: all 0.3s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.input-box:focus-within {
  border-color: #6a85b6;
  box-shadow: 0 8px 32px rgba(106, 133, 182, 0.18);
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  padding: 0;
  resize: none;
  font-size: 22px;
  line-height: 1.7;
  box-shadow: none;
  background: transparent;
  min-height: 48px;
  max-height: 180px;
}

.message-input :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-tools {
  display: flex;
  align-items: center;
  gap: 18px;
}

.tool-btn {
  color: #6a85b6;
  padding: 14px;
  border-radius: 12px;
  font-size: 28px;
  transition: all 0.3s ease;
}

.tool-btn:hover {
  background: #e3e8f7;
  color: #3b5998;
}

.send-btn {
  border-radius: 16px;
  padding: 14px 36px;
  background: linear-gradient(135deg, #6a85b6 0%, #bac8e0 100%);
  border: none;
  font-size: 22px;
  font-weight: 700;
  transition: all 0.3s ease;
}

.send-btn:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 8px 20px rgba(106, 133, 182, 0.18);
}

.send-btn:disabled {
  opacity: 0.5;
  transform: none;
  box-shadow: none;
}

.emoji-picker {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 20px;
  box-shadow: 0 16px 48px rgba(106, 133, 182, 0.13);
  border: 1.5px solid rgba(106, 133, 182, 0.10);
  margin-bottom: 18px;
  z-index: 100;
  max-height: 400px;
  overflow-y: auto;
}

.emoji-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1.5px solid rgba(106, 133, 182, 0.08);
  font-weight: 700;
  color: #3b5998;
  font-size: 20px;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 10px;
  padding: 20px;
}

.emoji-item {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.emoji-item:hover {
  background: #e3e8f7;
  transform: scale(1.13);
}
</style>
