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
    backgroundColor: '#FFFFFF',
    borderStyle: 'white',
    list: [
      {
        pagePath: 'pages/create/index',
        text: '首页',
        iconPath: 'assets/tabs/home-off.png',
        selectedIconPath: 'assets/tabs/home-on.png'
      },
      {
        pagePath: 'pages/quiz/index',
        text: '闯关',
        iconPath: 'assets/tabs/quiz-off.png',
        selectedIconPath: 'assets/tabs/quiz-on.png'
      },
      {
        pagePath: 'pages/report/index',
        text: '报告',
        iconPath: 'assets/tabs/report-off.png',
        selectedIconPath: 'assets/tabs/report-on.png'
      },
      {
        pagePath: 'pages/wrong/index',
        text: '错题',
        iconPath: 'assets/tabs/wrong-off.png',
        selectedIconPath: 'assets/tabs/wrong-on.png'
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
        iconPath: 'assets/tabs/profile-off.png',
        selectedIconPath: 'assets/tabs/profile-on.png'
      }
    ]
  }
})
