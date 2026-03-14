<script setup>
import { ref, computed } from 'vue'

const locale = ref('it') // 'it' or 'en'
const showLangMenu = ref(false)

const dynamicTranslations = ref({
  it: {} // Will be fetched from backend
})

const fetchBaseTranslations = async () => {
  try {
    const response = await fetch('/api/base-translations')
    if (response.ok) {
      dynamicTranslations.value.it = await response.json()
    }
  } catch (err) {
    console.error("Errore nel caricamento traduzioni base:", err)
  }
}

const t = (key) => {
  const table = dynamicTranslations.value[locale.value] || dynamicTranslations.value.it
  return table[key] || key
}

const inputMessage = ref('')
const isClassifying = ref(false)
const classificationResult = ref(null)
const classificationData = ref(null)

// Simuliamo un database in memoria per le richieste
const allRequests = ref([]) 

const fetchTickets = async () => {
  try {
    const response = await fetch('/api/tickets')
    if (response.ok) {
      allRequests.value = await response.json()
    }
  } catch (err) {
    console.error("Errore nel recupero ticket:", err)
  }
}

// Carica i dati all'avvio
import { onMounted } from 'vue'
onMounted(() => {
  fetchTickets()
  fetchBaseTranslations()
})

const categories = [
  { id: 'task', label: 'Task', desc: 'General work item', icon: '📝', color: '#3b82f6' },
  { id: 'bug', label: 'Bug', desc: 'Defect / error', icon: '🐛', color: '#ef4444' },
  { id: 'enhancement', label: 'Enhancement', desc: 'Feature extension', icon: '✨', color: '#10b981' },
  { id: 'research', label: 'Research', desc: 'Investigation / feasibility', icon: '🔬', color: '#8b5cf6' },
  { id: 'design', label: 'Design', desc: 'UI/UX / mockup', icon: '🎨', color: '#ec4899' },
  { id: 'testing', label: 'Testing', desc: 'QA / validation', icon: '🧪', color: '#f59e0b' },
  { id: 'deployment', label: 'Deployment', desc: 'Release / infra / CI-CD', icon: '🚀', color: '#06b6d4' },
  { id: 'documentation', label: 'Documentation', desc: 'Docs / guide', icon: '📚', color: '#64748b' }
]

const getCategoryInfo = (id) => {
  return categories.find(c => c.id === id) || null
}

const classifyMessage = async () => {
  if (!inputMessage.value.trim()) return;

  isClassifying.value = true
  classificationResult.value = null
  classificationData.value = null

  try {
    console.log("Classifying: ", inputMessage.value)
    const response = await fetch('/api/classify', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ prompt: inputMessage.value })
    })

    if (!response.ok) {
      console.error(`Errore classificatore: ${response.status} ${response.statusText}`)
      throw new Error(`Errore HTTP: ${response.status}`)
    }
    
    const data = await response.json()
    console.log("Classifier Response: ", data)
    classificationResult.value = data.category.toLowerCase()
    classificationData.value = data
  } catch (err) {
    console.error("Fallita comunicazione col backend. Uso mock:", err);
    console.warn("Modalità fallback Demo attiva.");
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const text = inputMessage.value.toLowerCase();
    let computedCategory = 'task';
    
    if (text.match(/(bug|errore|rotto|non va|crash|fallisce)/)) computedCategory = 'bug';
    else if (text.match(/(design|mockup|ui|ux|colore|grafica)/)) computedCategory = 'design';
    else if (text.match(/(aggiungere|nuovo|migliorare|feature|funzionalità)/)) computedCategory = 'enhancement';
    else if (text.match(/(test|verificare|validazione|qa)/)) computedCategory = 'testing';
    else if (text.match(/(deploy|rilascio|produzione|server|ci\/cd)/)) computedCategory = 'deployment';
    else if (text.match(/(doc|guida|manuale|scrivere)/)) computedCategory = 'documentation';
    else if (text.match(/(ricerca|fattibilità|scoprire|studiare)/)) computedCategory = 'research';

    classificationResult.value = computedCategory;
    classificationData.value = {
      original: inputMessage.value,
      translation: inputMessage.value,
      source_lang: '',
      target_lang: 'en',
      category: computedCategory,
      confidence: 'medium',
      urgency: 'Medium'
    };
  } finally {
    isClassifying.value = false;
    
    // Aggiorna la lista dei ticket dal database
    fetchTickets();
  }
}

const resetForm = () => {
  inputMessage.value = ''
  classificationResult.value = null
  classificationData.value = null
}

// Ticket grouping removed as dashboard is no longer present
</script>

<template>
  <main class="app-container">
    <header class="app-header">
      <div class="header-content">
        <div class="logo-box">
          <span class="logo-emoji">🧠</span>
        </div>
        <div class="header-text">
          <h1>{{ t('header_title') }}</h1>
          <p>{{ t('header_subtitle') }}</p>
        </div>
      </div>

      <div class="header-actions">
        <a href="http://localhost:8000/admin/" target="_blank" class="admin-link-btn">
          {{ t('django_admin') }}
        </a>
      </div>
    </header>

    <!-- VISTA CUSTOMER -->
    <div class="layout-grid">
      <section class="glass-panel input-section">
        <div class="panel-header">
          <h2>{{ t('new_request') }}</h2>
          <div class="pulse-indicator" :class="{ active: isClassifying }"></div>
        </div>
        
        <label for="message-input">{{ t('describe_problem') }}</label>
        <textarea
          id="message-input"
          v-model="inputMessage"
          :placeholder="t('placeholder_textarea')"
          rows="6"
          :disabled="classificationResult !== null"
        ></textarea>
        
        <div v-if="!classificationResult" class="action-buttons">
          <button 
            class="submit-button" 
            @click="classifyMessage" 
            :disabled="isClassifying || !inputMessage.trim()"
            :class="{ 'is-loading': isClassifying }"
          >
            <span class="btn-text" v-if="!isClassifying">
              {{ t('submit_btn') }}
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-send"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </span>
            <span class="btn-text" v-else>
              <span class="spinner"></span> {{ t('analyzing') }}
            </span>
          </button>
        </div>
        
        <div v-else class="action-buttons">
           <button class="submit-button secondary" @click="resetForm">
             {{ t('send_another') }}
           </button>
        </div>

        <transition name="fade-slide">
          <div class="result-card" v-if="classificationResult && !isClassifying">
            <h3 class="result-title">{{ t('classified_title') }}</h3>
            <p style="margin-bottom: 15px; color: var(--text-muted); font-size: 0.9rem;">
              {{ t('classified_text') }}
            </p>

            <!-- Translation details -->
            <div v-if="classificationData" class="translation-details">
              <div class="detail-row">
                <span class="detail-label">Original:</span>
                <span class="detail-value">{{ classificationData.original }}</span>
              </div>
              <div class="detail-row" v-if="classificationData.translation && classificationData.translation !== classificationData.original">
                <span class="detail-label">Translation:</span>
                <span class="detail-value">{{ classificationData.translation }}</span>
              </div>
              <div class="detail-row" v-if="classificationData.source_lang">
                <span class="detail-label">Language:</span>
                <span class="detail-value">{{ classificationData.source_lang }} → {{ classificationData.target_lang }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Confidence:</span>
                <span class="detail-value confidence-badge" :class="'confidence-' + classificationData.confidence">{{ classificationData.confidence }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Urgency:</span>
                <span class="detail-value urgency-badge" :class="'urgency-' + (classificationData.urgency || 'Medium').toLowerCase()">{{ classificationData.urgency || 'Medium' }}</span>
              </div>
            </div>

            <div 
              class="result-badge" 
              :style="{ 
                '--badge-color': getCategoryInfo(classificationResult)?.color,
                backgroundColor: getCategoryInfo(classificationResult)?.color + '15',
                borderColor: getCategoryInfo(classificationResult)?.color + '40'
              }"
            >
              <span class="result-icon-large">{{ getCategoryInfo(classificationResult)?.icon }}</span>
              <div class="result-info">
                <strong>{{ t('cat_' + classificationResult) }}</strong>
                <span>{{ t('forwarded_to') }} {{ t('cat_' + classificationResult) }}</span>
              </div>
            </div>
          </div>
        </transition>
      </section>

      <section class="glass-panel info-section">
        <div class="panel-header">
          <h2>{{ t('how_it_works') }}</h2>
        </div>
        <p class="sub-text">{{ t('how_it_works_text') }}</p>
        
        <div class="info-illustration">
          <div class="illus-box">{{ t('step_you') }}</div>
          <div class="illus-arrow">➔</div>
          <div class="illus-box highlight">{{ t('step_ia') }}</div>
          <div class="illus-arrow">➔</div>
          <div class="illus-box">{{ t('step_res') }}</div>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
/* BASE STYLES */
.app-container {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2.5rem;
  animation: slideDown 0.6s ease-out;
  flex-wrap: wrap;
  gap: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* Language Selector */
.lang-selector {
  position: relative;
}

.lang-btn {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--surface-border);
  color: white;
  padding: 8px 14px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.3s;
}

.lang-btn:hover {
  background: var(--surface-border);
}

.lang-btn .flag {
  font-size: 1.2rem;
}

.lang-btn .chevron {
  opacity: 0.5;
  transition: transform 0.3s;
}

.lang-btn .chevron.open {
  transform: rotate(180deg);
}

.lang-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--surface);
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  padding: 6px;
  min-width: 140px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  z-index: 100;
  backdrop-filter: blur(10px);
}

.lang-dropdown button {
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
}

.lang-dropdown button:hover {
  background: rgba(255,255,255,0.05);
  color: white;
}

/* Toggle Views */
.view-toggle {
  display: flex;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--surface-border);
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.view-toggle button {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-toggle button:hover {
  color: white;
}

.view-toggle button.active {
  background: var(--surface-border);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.admin-link-btn {
  text-decoration: none;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  border: 1px solid transparent;
}

.admin-link-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-color: rgba(255, 255, 255, 0.2);
}

.logo-box {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
}

.header-text h1 {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(to right, #fff, #a5b4fc);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-text p {
  color: var(--text-muted);
  font-weight: 400;
  margin-top: 4px;
}

.layout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

@media (max-width: 900px) {
  .layout-grid { grid-template-columns: 1fr; }
  .app-header { flex-direction: column; align-items: flex-start; }
  .view-toggle { width: 100%; justify-content: stretch; }
  .view-toggle button { flex: 1; justify-content: center; }
}

.glass-panel {
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--surface-border);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

.input-section { animation-delay: 0.1s; }
.info-section { animation-delay: 0.2s; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
}

.pulse-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: all 0.3s;
}

.pulse-indicator.active {
  background: var(--success);
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 1.5s infinite;
}

label {
  font-size: 0.875rem;
  color: #cbd5e1;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

textarea {
  width: 100%;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  color: #fff;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

textarea:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.submit-button {
  flex: 1;
  padding: 1rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-button.secondary {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
}

.submit-button.secondary:hover {
  background: rgba(255,255,255,0.1);
}

.submit-button:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4); }
.submit-button:active:not(:disabled) { transform: scale(0.98); }
.submit-button:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-text {
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.result-card {
  margin-top: 2rem;
  background: rgba(0,0,0,0.2);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255,255,255,0.05);
}

.result-title {
  font-size: 0.875rem;
  color: var(--success);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 0.5rem;
/* Translation details */
.translation-details {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  font-size: 0.875rem;
}

.detail-label {
  color: var(--text-muted);
  font-weight: 500;
  min-width: 90px;
  flex-shrink: 0;
}

.detail-value {
  color: #e2e8f0;
  word-break: break-word;
}

.confidence-badge, .urgency-badge {
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.confidence-high { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.confidence-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.confidence-low { background: rgba(239, 68, 68, 0.2); color: #f87171; }

.urgency-critical { background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }
.urgency-high { background: rgba(249, 115, 22, 0.2); color: #fb923c; }
.urgency-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.urgency-low { background: rgba(16, 185, 129, 0.2); color: #34d399; }

.result-badge {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid;
}

.result-icon-large { font-size: 2rem; }
.result-info strong { display: block; font-size: 1.25rem; color: var(--badge-color); }
.result-info span { font-size: 0.875rem; color: #cbd5e1; }

.sub-text {
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

/* Info Illustration */
.info-illustration {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 2rem 1.5rem;
  background: rgba(0,0,0,0.2);
  border-radius: 16px;
  border: 1px dashed rgba(255,255,255,0.1);
}

.illus-box {
  background: rgba(255,255,255,0.05);
  padding: 12px 16px;
  border-radius: 12px;
  font-weight: 500;
  border: 1px solid rgba(255,255,255,0.1);
  text-align: center;
  font-size: 0.9rem;
}

.illus-box.highlight {
  background: rgba(99, 102, 241, 0.2);
  border-color: var(--primary);
  color: #fff;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
}

.illus-arrow { color: var(--text-muted); font-size: 1.2rem; }

/* ADMIN DASHBOARD */
.admin-dashboard {
  animation: slideUp 0.5s ease-out forwards;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  background: var(--surface);
  padding: 1.5rem 2rem;
  border-radius: 16px;
  border: 1px solid var(--surface-border);
  gap: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.admin-view-toggle {
  display: flex;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--surface-border);
  border-radius: 10px;
  padding: 4px;
}

.admin-view-toggle button {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 6px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.admin-view-toggle button.active {
  background: var(--primary);
  color: white;
}

.admin-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.stats-badge {
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #a5b4fc;
}

/* TABLE VIEW */
.admin-table-container {
  background: var(--surface);
  border-radius: 20px;
  border: 1px solid var(--surface-border);
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.admin-table th {
  background: rgba(255,255,255,0.03);
  padding: 1rem 1.5rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--surface-border);
}

.admin-table td {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 0.95rem;
}

.td-id { font-family: monospace; color: var(--text-muted); }
.td-time { color: var(--text-muted); white-space: nowrap; }
.td-text { max-width: 300px; overflow: hidden; text-overflow: ellipsis; }
.td-reasoning { font-size: 0.85rem; color: #cbd5e1; max-width: 250px; }

.table-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

.confidence-tag {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.confidence-tag.high { background: rgba(16, 185, 129, 0.1); color: var(--success); }
.confidence-tag.medium { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.confidence-tag.low { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

.empty-state {
  text-align: center;
  padding: 6rem 2rem;
  background: var(--surface);
  border-radius: 24px;
  border: 1px dashed rgba(255,255,255,0.1);
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.5;
  margin-bottom: 1rem;
  display: inline-block;
}

.admin-kanban {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  align-items: start;
}

.kanban-column {
  background: var(--surface);
  border-radius: 16px;
  border: 1px solid var(--surface-border);
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 3px solid;
  padding-top: 15px;
}

.col-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.col-title h3 {
  font-size: 1.1rem;
  margin: 0;
  font-weight: 600;
}

.col-count {
  background: rgba(255,255,255,0.1);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 700;
}

.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 5px;
}

/* Scrollbar personalizzata per le colonne */
.ticket-list::-webkit-scrollbar { width: 6px; }
.ticket-list::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); border-radius: 10px; }
.ticket-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

.ticket-card {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(255,255,255,0.05);
  padding: 1.25rem;
  border-radius: 12px;
  transition: all 0.2s;
}

.ticket-card:hover {
  transform: translateY(-3px);
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.15);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.ticket-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-bottom: 8px;
  font-weight: 500;
}

.ticket-text {
  font-size: 0.95rem;
  line-height: 1.5;
  color: #e2e8f0;
  font-style: italic;
}

/* ANIMATIONS */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.4s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }

/* POP ANIMATION */
.pop-enter-active, .pop-leave-active { transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.pop-enter-from, .pop-leave-to { opacity: 0; transform: scale(0.9) translateY(-10px); }
</style>
