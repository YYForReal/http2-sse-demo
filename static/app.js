console.log('HTTP/2 Server Push Demo')
document.addEventListener('DOMContentLoaded', () => {
  const timeElement = document.getElementById('load-time')
  if (timeElement) {
    timeElement.textContent = `页面加载完成时间: ${new Date().toLocaleTimeString()}`
  }
})