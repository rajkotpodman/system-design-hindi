<template>
  <div class="gt-wrapper">
    <span class="gt-icon" title="Translate into 180+ World Languages">🌐</span>
    <div id="google_translate_element"></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

function initTranslate() {
  if (typeof window === 'undefined') return
  if (window.google && window.google.translate && window.google.translate.TranslateElement) {
    const el = document.getElementById('google_translate_element')
    if (el && (!el.hasChildNodes() || el.innerHTML.trim() === '')) {
      new window.google.translate.TranslateElement({
        pageLanguage: 'auto',
        autoDisplay: false
      }, 'google_translate_element')
    }
  }

  // Bind change event to sync googtrans cookie
  const checkCombo = setInterval(() => {
    const combo = document.querySelector('.goog-te-combo')
    if (combo) {
      clearInterval(checkCombo)
      if (!combo.dataset.bound) {
        combo.dataset.bound = 'true'
        combo.addEventListener('change', () => {
          const val = combo.value
          if (val) {
            document.cookie = `googtrans=/auto/${val}; path=/;`
            document.cookie = `googtrans=/auto/${val}; path=/; domain=${location.hostname};`
          } else {
            document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
            document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${location.hostname};`
          }
        })
      }
    }
  }, 200)
  setTimeout(() => clearInterval(checkCombo), 5000)
}

onMounted(() => {
  window.googleTranslateElementInit = initTranslate

  if (!document.getElementById('google-translate-script')) {
    const script = document.createElement('script')
    script.id = 'google-translate-script'
    script.type = 'text/javascript'
    script.async = true
    script.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'
    document.body.appendChild(script)
  } else {
    setTimeout(initTranslate, 300)
  }
})
</script>

<style scoped>
.gt-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 8px;
}
.gt-icon {
  font-size: 1rem;
}
</style>
