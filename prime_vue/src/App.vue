<template>
  <div id="app">
    <div class="app-header">
      <div class="container">
        <h1 class="app-title">Clinical RNA-seq Data Explorer</h1>
        <p class="app-subtitle">Explore and analyze RNA sequencing datasets</p>
      </div>
    </div>

    <div class="container main-content">
      <DataViewer />
    </div>

    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 RNA-seq Data Explorer</p>
      </div>
    </footer>
  </div>
</template>

<script>
import DataViewer from './components/DataViewer.vue'

export default {
  name: 'App',
  components: {
    DataViewer
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
  width: 100%;
}

.app-header {
  background: linear-gradient(120deg, #42b883 0%, #2f9c6a 100%);
  color: white;
  padding: 2rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.app-title {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 600;
}

.app-subtitle {
  margin: 0.5rem 0 0 0;
  font-size: 1.2rem;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.app-footer {
  background-color: #f8f9fa;
  padding: 1.5rem 0;
  margin-top: 2rem;
  color: #6c757d;
  font-size: 0.9rem;
  text-align: center;
}
</style>
