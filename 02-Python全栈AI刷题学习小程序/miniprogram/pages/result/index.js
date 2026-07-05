Page({
  data: {
    score: 0
  },

  onLoad(options) {
    this.setData({
      score: Number(options.score || 0)
    })
  }
})

