import Home from './views/Home.vue'
import SoilMap from './views/SoilMap.vue'
import SoilAnalysis from './views/SoilAnalysis.vue'
import EarthworkCalculation from './views/EarthworkCalculation.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/soil-map',
    name: 'SoilMap',
    component: SoilMap
  },
  {
    path: '/soil-analysis',
    name: 'SoilAnalysis',
    component: SoilAnalysis
  },
  {
    path: '/earthwork-calculation',
    name: 'EarthworkCalculation',
    component: EarthworkCalculation
  }
]

export default routes