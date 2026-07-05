Page({
  data: {
    levelId: '',
    questions: [],
    loading: true
  },

  onLoad(options) {
    const app = getApp()
    const levelId = options.levelId || 'level-1'
    this.setData({ levelId })
    wx.request({
      url: `${app.globalData.apiBaseUrl}/api/questions?levelId=${levelId}`,
      success: (res) => {
        this.setData({
          questions: res.data.data || [],
          loading: false
        })
      }
    })
  },

  finish() {
    wx.navigateTo({
      url: '/pages/result/index?score=1'
    })
  }
})

