export const NotificationPlugin = async ({ project }) => {
  const NOTIFY_URL = "http://192.168.3.18:5000/notify"
  
  const notify = async (title, body) => {
    try {
      const response = await fetch(NOTIFY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title,
          body: body,
          sound: "default"
        })
      })
      return response.ok
    } catch (error) {
      console.error("Notification failed:", error.message)
      return false
    }
  }
  
  const truncate = (str, len = 80) => {
    return str && str.length > len ? str.substring(0, len) + "..." : str || ""
  }
  
  return {
    "session.idle": async ({ session }) => {
      const projectName = project?.name || "未知项目"
      await notify("✅ OpenCode 任务完成", `项目: ${projectName}`)
    },
    
    "session.error": async ({ session, error }) => {
      const errorMsg = truncate(error?.message || "未知错误")
      await notify("❌ OpenCode 任务失败", errorMsg)
    },
    
    "permission.asked": async ({ permission }) => {
      const desc = truncate(permission?.description || "需要权限确认")
      await notify("⚠️ OpenCode 需要权限", desc)
    },
    
    "tool.execute.before": async (input, output) => {
      if (input.tool === "question") {
        const questions = output?.args?.questions || []
        const questionText = questions[0]?.question || "等待回复"
        const summary = truncate(questionText)
        await notify("❓ OpenCode 等待回复", summary)
      }
    }
  }
}