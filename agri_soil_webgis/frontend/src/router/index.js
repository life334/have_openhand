import Home from '../views/Home.vue'
import SoilMap from '../views/SoilMap.vue'
import SoilAnalysis from '../views/SoilAnalysis.vue'
import CropSuitability from '../views/CropSuitability.vue'
import ErosionRisk from '../views/ErosionRisk.vue'
import DataManagement from '../views/DataManagement.vue'
import EarthworkCalculation from '../views/EarthworkCalculation.vue'
import TINEarthworkCalculation from '../views/TINEarthworkCalculation.vue'

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
    path: '/crop-suitability',
    name: 'CropSuitability',
    component: CropSuitability
  },
  {
    path: '/erosion-risk',
    name: 'ErosionRisk',
    component: ErosionRisk
  },
  {
    path: '/data-management',
    name: 'DataManagement',
    component: DataManagement
  },
  {
    path: '/earthwork-calculation',
    name: 'EarthworkCalculation',
    component: EarthworkCalculation
  },
  {
    path: '/tin-earthwork-calculation',
    name: 'TINEarthworkCalculation',
    component: TINEarthworkCalculation
  }
]

export default routes