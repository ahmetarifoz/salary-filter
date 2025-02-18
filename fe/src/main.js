// main.js
import { createApp } from 'vue'
import App from './App.vue'

// 1) Vuetify importları
import 'vuetify/styles'
import { createVuetify } from 'vuetify'

// Vuetify 3: Tüm bileşenleri ve direktifleri otomatik kullanmak için:
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'


import { aliases, mdi } from 'vuetify/iconsets/mdi'

// 2) Vuetify instance
const vuetify = createVuetify({
  components,  // <-- bileşenleri ekle
  directives,  // <-- direktifleri ekle
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  },
  theme: {
    defaultTheme: 'light', // 'dark' olarak değiştirebilirsin
  },
})

// 3) Vue uygulamasını başlat
createApp(App)
  .use(vuetify)
  .mount('#app')
