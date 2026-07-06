export default defineAppConfig({
  pages: [
    'pages/create/index',
    'pages/quiz/index',
    'pages/report/index',
    'pages/wrong/index',
    'pages/profile/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#6246F2',
    navigationBarTitleText: '水母 DIY 学习助手',
    navigationBarTextStyle: 'white',
    navigationStyle: 'custom'
  },
  tabBar: {
    color: '#6B7280',
    selectedColor: '#6246F2',
    backgroundColor: '#FFFDF7',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/create/index',
        text: '首页'
      },
      {
        pagePath: 'pages/quiz/index',
        text: '闯关'
      },
      {
        pagePath: 'pages/report/index',
        text: '报告'
      },
      {
        pagePath: 'pages/wrong/index',
        text: '错题'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的'
      }
    ]
  }
})
