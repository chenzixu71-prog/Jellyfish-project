export default defineAppConfig({
  pages: [
    'pages/create/index',
    'pages/quiz/index',
    'pages/report/index',
    'pages/profile/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#FFFDF4',
    navigationBarTitleText: '水母diy学习助手',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    color: '#6B7280',
    selectedColor: '#1767C8',
    backgroundColor: '#FFFFFF',
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
