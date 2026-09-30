import React from "react";
import { Check, LogOut } from "lucide-react";
import { Button, Notice } from "../components/UI";
import { useAccount } from "../hooks/useAccount";
import { PLANS, planById } from "../plans.mjs";

export function Plans() {
  const account = useAccount();
  const current = planById(account.role);

  return (
    <main id="main-content" className="information-page container">
      <span className="eyebrow">ELIGE CÓMO USAR ATLAS</span>
      <h1>
        Tres formas de consultar.
        <br />
        <em>Una sola evidencia.</em>
      </h1>
      <p className="page-lead">
        Básico, Profesional y MAX describen la cuenta. Elige el que vas a usar.
      </p>
      <Notice>
        Versión de demostración: la selección de planes es gratuita y no realiza
        cobros. Los precios mostrados son de referencia; todavía no hay contratación en línea.
      </Notice>
      {!account.configured && <Notice tone="warning">{account.error}</Notice>}
      {account.ready && !account.user && (
        <Notice>
          Para elegir un plan, <a href="#/acceso">inicia sesión o crea una cuenta</a>.
        </Notice>
      )}
      {account.ready && account.user && (
        <div className="plans-session">
          <p>
            Sesión de <strong>{account.user.email}</strong>
            {current ? `. Plan actual: ${current.name}.` : "."}
          </p>
          <Button icon={LogOut} variant="outline" onClick={account.leave} disabled={account.busy}>
            Cerrar sesión
          </Button>
        </div>
      )}
      {account.ready && account.user && account.error && (
        <p className="plans-error" role="alert">
          {account.error}
        </p>
      )}
      {!account.ready && <p>Revisando la cuenta…</p>}
      <div className="plans-grid">
        {PLANS.map((plan) => {
          const active = account.role === plan.id;
          return (
            <article
              className={active ? "plan-card is-current" : "plan-card"}
              key={plan.id}
            >
              <span className="eyebrow">{plan.audience}</span>
              <h2>{plan.name}</h2>
              <p className="plan-cost">
                {plan.price ? (
                  <>
                    <span className="plan-amount">{plan.price.amount}</span>
                    <span className="plan-period">{plan.price.detail}</span>
                  </>
                ) : (
                  plan.cost
                )}
              </p>
              <p>{plan.summary}</p>
              <ul>
                {plan.includes.map((item) => (
                  <li key={item}>
                    <Check size={16} aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
              {account.user ? (
                <Button
                  variant={active ? "outline" : "primary"}
                  disabled={active || account.busy || !account.configured}
                  onClick={() => account.choose(plan.id)}
                >
                  {active ? "Plan actual" : "Probar este plan"}
                </Button>
              ) : (
                <a className="button button-primary" href="#/acceso">
                  Entra para elegir
                </a>
              )}
            </article>
          );
        })}
      </div>
      <Notice>
        Precios de referencia por persona: Profesional, $399 MXN al mes;
        MAX, $799 MXN al mes. Esta demostración no cobra ni solicita datos de pago.
      </Notice>
    </main>
  );
}
