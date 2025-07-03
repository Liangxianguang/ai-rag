import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

// 文件处理工具
export function useFileHandler() {
  const fileInputRef = ref(null)

  // 格式化文件大小
  function formatSize(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 处理文件上传
  function handleFileUpload() {
    if (!fileInputRef.value) return
    fileInputRef.value.click()
  }

  // 文件选择处理
  function onFileSelected(event, onFileProcessed) {
    const files = event.target.files
    if (!files || files.length === 0) return
    
    const file = files[0]
    
    // 检查文件大小 (限制10MB)
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error('文件大小不能超过10MB')
      return
    }
    
    // 检查文件类型
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'image/webp',
      'text/plain', 'text/markdown', 'application/pdf',
      'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if (!allowedTypes.includes(file.type)) {
      ElMessage.error('不支持的文件类型。支持图片、文本、PDF、Word文档')
      return
    }
    
    // 处理图片文件
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const imageUrl = e.target.result
        const imageMessage = {
          type: 'user',
          content: `[图片: ${file.name}]`,
          imageUrl: imageUrl,
          timestamp: Date.now()
        }
        onFileProcessed(imageMessage)
        ElMessage.success(`已上传图片: ${file.name}`)
      }
      reader.readAsDataURL(file)
    } 
    // 处理文本文件
    else if (file.type.startsWith('text/') || file.type === 'application/pdf') {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target.result
        const fileContent = `\n\n[文件: ${file.name}]\n${content.substring(0, 1000)}${content.length > 1000 ? '...' : ''}`
        onFileProcessed(null, fileContent)
        ElMessage.success(`已读取文件: ${file.name}`)
      }
      reader.readAsText(file)
    } else {
      // 其他文件类型，显示文件信息
      const fileMessage = {
        type: 'user',
        content: `[文件: ${file.name}] (${(file.size / 1024 / 1024).toFixed(2)}MB)`,
        timestamp: Date.now()
      }
      onFileProcessed(fileMessage)
      ElMessage.success(`已上传文件: ${file.name}`)
    }
    
    // 清空文件选择
    event.target.value = ''
  }

  return {
    fileInputRef,
    formatSize,
    handleFileUpload,
    onFileSelected
  }
}

// 表情工具
export function useEmoji() {
  const showEmojiPicker = ref(false)

  // 常用表情数据
  const commonEmojis = [
    '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇',
    '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚',
    '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩',
    '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
    '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬',
    '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗',
    '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯',
    '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐',
    '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉',
    '👆', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏', '🙌',
    '🤝', '🙏', '✍️', '💪', '❤️', '🧡', '💛', '💚', '💙', '💜',
    '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖'
  ]

  // 插入表情
  function insertEmoji(emoji, msgRef) {
    msgRef.value += emoji
    showEmojiPicker.value = false
    // 聚焦到输入框
    nextTick(() => {
      const textarea = document.querySelector('.message-input textarea')
      if (textarea) {
        textarea.focus()
      }
    })
  }

  return {
    showEmojiPicker,
    commonEmojis,
    insertEmoji
  }
}

// 文本处理工具
export function useTextUtils() {
  // 格式化答案
  function formatAnswer(text) {
    return text.replace(/\n/g, '<br>')
  }

  // 复制文本
  function copyText(text) {
    navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  }

  // 点赞消息
  function likeMessage(index) {
    ElMessage.success('感谢您的反馈！')
  }

  // 重新生成回复
  function regenerateResponse(index) {
    ElMessage.info('重新生成功能开发中...')
  }

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

  return {
    formatAnswer,
    copyText,
    likeMessage,
    regenerateResponse,
    handleInput
  }
}
