import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config'

// PrimeVue Components
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import Message from 'primevue/message'
import Card from 'primevue/card'

// PrimeVue Styles
import 'primevue/resources/themes/saga-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

const app = createApp(App)

// Use PrimeVue
app.use(PrimeVue, { ripple: true })

// Register PrimeVue Components
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Dropdown', Dropdown)
app.component('InputText', InputText)
app.component('Button', Button)
app.component('ProgressSpinner', ProgressSpinner)
app.component('Message', Message)
app.component('Card', Card)

app.mount('#app')
