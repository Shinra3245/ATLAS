import React from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/manrope/latin-400.css";
import "@fontsource/manrope/latin-500.css";
import "@fontsource/manrope/latin-600.css";
import "@fontsource/manrope/latin-700.css";
import "@fontsource/manrope/latin-800.css";
import App from "./App";
import { LoaderShowcase } from "./pages/LoaderShowcase";
import "./styles.css";
import "./print.css";

function ViewRouter() {
  const [preview, setPreview] = React.useState(
    () => window.location.hash === "#/loaders",
  );
  React.useEffect(() => {
    const update = () => setPreview(window.location.hash === "#/loaders");
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);
  return preview ? <LoaderShowcase /> : <App />;
}

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
      <ViewRouter />
    </ErrorBoundary>
  </React.StrictMode>,
);
