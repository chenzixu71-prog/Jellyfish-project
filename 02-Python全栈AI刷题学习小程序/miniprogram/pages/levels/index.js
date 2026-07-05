Page({
  data: {
    levels: [],
    loading: true,
    error: ''
  },

  onLoad() {
    const app = getApp()
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/levels`,
      success: (res) => {
        this.setData({
          levels: res.data.data || [],
          loading: false
        })
      },
      fail: () => {
        this.setData({
          error: '后端接口暂时无法访问',
          loading: false
        })
      }
    })
  },

  openQuiz(event) {
    const levelId = event.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/quiz/index?levelId=${levelId}`
    })
  }
})

