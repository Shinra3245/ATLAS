import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/manrope/latin-400.css";
import "@fontsource/manrope/latin-500.css";
import "@fontsource/manrope/latin-600.css";
import "@fontsource/manrope/latin-700.css";
import "@fontsource/manrope/latin-800.css";
import App from "./App";
import { AccountProvider } from "./hooks/useAccount";
import "./styles.css";
import "./public-ui.css";
import "./print.css";

class ErrorBoundary extends React.Component {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed)
      return (
        <main className="information-page container" role="alert">
          <h1>No pudimos mostrar esta vista</h1>
          <p>
            Ocurrió un error de interfaz. No se mostrarán resultados
            incompletos.
          </p>
          <button
            className="button button-primary"
            onClick={() => {
              window.location.hash = "/";
              window.location.reload();
            }}
          >
            Volver al inicio
          </button>
        </main>
      );
    return this.props.children;
  }
}
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AccountProvider>
        <App />
      </AccountProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);
