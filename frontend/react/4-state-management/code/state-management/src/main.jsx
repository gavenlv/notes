import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Provider as ReduxProvider } from 'react-redux'
import { store } from './store/reduxStore.js'
import { JotaiProvider } from './store/jotaiStore.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <JotaiProvider>
        <App />
      </JotaiProvider>
    </ReduxProvider>
  </React.StrictMode>,
)