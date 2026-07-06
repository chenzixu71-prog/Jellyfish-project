export default defineAppConfig({
  pages: [
    'pages/create/index',
    'pages/quiz/index',
    'pages/report/index',
    'pages/profile/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#6246F2',
    navigationBarTitleText: '水母 DIY 学习助手',
    navigationBarTextStyle: 'white'
  },
  tabBar: {
    color: '#6B7280',
    selectedColor: '#6246F2',
    backgroundColor: '#FFFDF7',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/create/index',
        text: '学习'
      },
      {
        pagePath: 'pages/profile/index',
        text: '记录'
      }
    ]
  }
})
