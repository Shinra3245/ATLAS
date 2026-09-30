import React, { useState } from "react";
import {
  ArrowRight, BarChart3, Building2, Eye, EyeOff, FileStack, Info,
  Layers3, LockKeyhole, LogIn, LogOut, Mail, MapPin, UserRound, UserRoundPlus,
} from "lucide-react";
import { Button, Logo, Notice } from "../components/UI";
import { useAccount } from "../hooks/useAccount";
import { TerritoryMap } from "../map/TerritoryMap";
import { planById } from "../plans.mjs";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const loginBenefits = [
  [BarChart3, "Decide con más contexto", "Consulta condiciones, fuentes y límites de la evidencia disponible."],
  [MapPin, "Explora localidades", "Selecciona localidades publicadas de Irapuato y Celaya."],
  [Layers3, "Visualiza y compara", "Contrasta dos localidades bajo los mismos criterios."],
];
const registerBenefits = [
  [BarChart3, "Análisis territorial", "Revisa factores y su evidencia para una localidad."],
  [Layers3, "Comparaciones", "Contrasta localidades y escenarios con criterios consistentes."],
  [FileStack, "Información trazable", "Consulta fuentes, fechas y datos que aún requieren validación."],
];

function AuthField({ id, label, icon: Icon, type = "text", hint, ...props }) {
  const [visible, setVisible] = useState(false);
  const password = type === "password";
  return (
    <div className="auth-field">
      <label htmlFor={id}>{label}</label>
      <div className="auth-input-wrap">
        <Icon size={19} aria-hidden="true" />
        <input id={id} type={password && visible ? "text" : type} {...props} />
        {password && (
          <button className="auth-reveal" type="button" aria-label={visible ? "Ocultar contraseña" : "Mostrar contraseña"} aria-pressed={visible} onClick={() => setVisible((value) => !value)}>
            {visible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {hint && <small className="auth-field-hint">{hint}</small>}
    </div>
  );
}

export function Access({ mode = "login" }) {
  const account = useAccount();
  const registering = mode === "register";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [institution, setInstitution] = useState("");
  const [remember, setRemember] = useState(true);
  const [accepted, setAccepted] = useState(false);
  const [reset, setReset] = useState(false);
  const [resetSent, setResetSent] = useState(false);
  const [localError, setLocalError] = useState(null);
  const current = planById(account.role);

  function update(setter) {
    return (event) => {
      setter(event.target.value);
      setLocalError(null);
    };
  }

  function validate() {
    if (registering && (fullName.trim().length < 2 || fullName.trim().length > 100))
      return "Escribe tu nombre completo (entre 2 y 100 caracteres).";
    if (!emailPattern.test(email.trim())) return "Escribe un correo electrónico válido.";
    if (registering && institution.trim().length > 0 && (institution.trim().length < 2 || institution.trim().length > 120))
      return "Escribe el nombre de tu institución u organización.";
    if (reset) return null;
    if (registering && (password.length < 8 || !/[a-zA-Z]/.test(password) || !/\d/.test(password)))
      return "La contraseña debe tener al menos 8 caracteres, con letras y números.";
    if (!registering && password.length < 6) return "Escribe tu contraseña.";
    if (registering && password !== confirmPassword) return "Las contraseñas no coinciden.";
    if (registering && !accepted) return "Lee y acepta el alcance preliminar de ATLAS.";
    return null;
  }

  async function submit(event) {
    event.preventDefault();
    const problem = validate();
    setLocalError(problem);
    if (problem || !account.configured) return;
    if (reset) {
      const sent = await account.resetPassword(email.trim());
      if (sent) setResetSent(true);
      return;
    }
    const result = registering
      ? await account.register(email.trim(), password, { fullName, institution })
      : await account.enter(email.trim(), password, remember);
    if (result) location.hash = registering ? "/planes" : "/sistema";
  }

  const benefits = registering ? registerBenefits : loginBenefits;
  return (
    <main id="main-content" className={`auth-page ${registering ? "auth-register" : "auth-login"}`}>
      <div className="auth-map" aria-hidden="true"><TerritoryMap mini locations={[]} /></div>
      <div className="auth-map-wash" aria-hidden="true" />
      <div className="auth-city auth-city-irapuato" aria-hidden="true"><span />Irapuato</div>
      <div className="auth-city auth-city-celaya" aria-hidden="true"><span />Celaya</div>
      <div className="auth-layout">
        <section className="auth-intro" aria-label="Acerca de ATLAS">
          <span className="auth-kicker"><MapPin size={16} /> Irapuato + Celaya</span>
          <h1>{registering ? <>Crea tu cuenta<br />en ATLAS</> : <>Accede a tu<br />análisis territorial</>}</h1>
          <p className="auth-intro-lead">
            {registering
              ? "Accede a análisis territoriales, compara localidades y consulta la evidencia disponible para Irapuato y Celaya."
              : "Explora información territorial de Irapuato y Celaya con criterios claros y evidencia a la vista."}
          </p>
          <div className="auth-benefits">
            {benefits.map(([Icon, title, description], index) => (
              <div className="auth-benefit" key={title}>
                <span className={`auth-benefit-icon auth-benefit-icon-${index + 1}`}><Icon size={24} /></span>
                <span><strong>{title}</strong><small>{description}</small></span>
              </div>
            ))}
          </div>
        </section>
        <section className="auth-card" aria-labelledby="auth-title">
          {!registering && <div className="auth-card-brand"><Logo /><span>Irapuato + Celaya</span></div>}
          <span className="auth-accent" aria-hidden="true" />
          {account.ready && account.user ? (
            <div className="auth-signed-in">
              <h2 id="auth-title">Tu cuenta está activa</h2>
              <p>Sesión de <strong>{account.user.email}</strong>{current ? `. Plan ${current.name}.` : "."}</p>
              <a className="button button-primary auth-submit" href="#/sistema">Explorar ATLAS <ArrowRight size={18} /></a>
              <a className="button button-outline auth-secondary" href="#/planes">Ver planes</a>
              <Button variant="outline" icon={LogOut} onClick={account.leave} loading={account.busy}>Cerrar sesión</Button>
            </div>
          ) : (
            <>
              <h2 id="auth-title">{reset ? "Recuperar contraseña" : registering ? "Crear cuenta" : "Iniciar sesión"}</h2>
              <p className="auth-card-lead">
                {reset ? "Te enviaremos un enlace para restablecer tu contraseña." : registering ? "Regístrate para consultar análisis y gestionar tu cuenta." : "Accede a tu cuenta para continuar con tus consultas territoriales."}
              </p>
              {!account.configured && <Notice tone="warning">El acceso a cuentas no está disponible en este entorno.</Notice>}
              {!account.ready && <p className="auth-status">Revisando tu sesión…</p>}
              {resetSent ? (
                <div className="auth-reset-sent" role="status">
                  <Mail size={24} />
                  <p>Si el correo tiene una cuenta, recibirás las instrucciones para restablecer la contraseña.</p>
                  <a href="#/acceso" onClick={() => { setReset(false); setResetSent(false); setLocalError(null); }}>Volver a iniciar sesión</a>
                </div>
              ) : (
                <form className="auth-form" noValidate onSubmit={submit}>
                  {registering && <AuthField id="auth-name" label="Nombre completo *" icon={UserRound} placeholder="Ingresa tu nombre completo" autoComplete="name" maxLength={100} value={fullName} onChange={update(setFullName)} />}
                  <AuthField id="auth-email" label="Correo electrónico *" icon={Mail} type="email" placeholder="nombre@institucion.gob.mx" autoComplete="email" value={email} onChange={update(setEmail)} />
                  {registering && <AuthField id="auth-institution" label="Institución u organización (opcional)" icon={Building2} placeholder="Ej. Gobierno Municipal de Irapuato" autoComplete="organization" maxLength={120} value={institution} onChange={update(setInstitution)} />}
                  {!reset && <AuthField id="auth-password" label="Contraseña *" icon={LockKeyhole} type="password" placeholder={registering ? "Crea una contraseña" : "Ingresa tu contraseña"} autoComplete={registering ? "new-password" : "current-password"} value={password} onChange={update(setPassword)} hint={registering ? "Mínimo 8 caracteres, con letras y números." : undefined} />}
                  {registering && <AuthField id="auth-confirm" label="Confirmar contraseña *" icon={LockKeyhole} type="password" placeholder="Repite tu contraseña" autoComplete="new-password" value={confirmPassword} onChange={update(setConfirmPassword)} />}
                  {!registering && !reset && <div className="auth-options"><label className="auth-check"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />Recordarme</label><button type="button" className="auth-text-link" onClick={() => { setReset(true); setLocalError(null); }}>¿Olvidaste tu contraseña?</button></div>}
                  {registering && <label className="auth-check auth-terms"><input type="checkbox" checked={accepted} onChange={(event) => setAccepted(event.target.checked)} /><span>He leído el <a href="#/metodologia" target="_blank" rel="noopener noreferrer">alcance y las limitaciones</a> de esta evaluación preliminar.</span></label>}
                  {(localError || account.error && account.configured) && <p className="auth-error" role="alert">{localError || account.error}</p>}
                  <Button type="submit" className="auth-submit" loading={account.busy} disabled={!account.configured || !account.ready} icon={reset ? Mail : registering ? UserRoundPlus : LogIn}>{reset ? "Enviar enlace" : registering ? "Crear cuenta" : "Iniciar sesión"}<ArrowRight size={18} aria-hidden="true" /></Button>
                </form>
              )}
              {reset ? <button className="auth-back" type="button" onClick={() => { setReset(false); setResetSent(false); setLocalError(null); }}>Volver a iniciar sesión</button> : (
                <>
                  {!registering && <div className="auth-divider"><span>o continúa con</span></div>}
                  {registering ? <div className="auth-switch">¿Ya tienes cuenta? <a href="#/acceso">Inicia sesión</a></div> : <a className="button button-outline auth-secondary" href="#/registro"><UserRoundPlus size={19} /> Crear cuenta</a>}
                </>
              )}
              <div className="auth-disclaimer"><Info size={19} aria-hidden="true" /><span>Evaluación preliminar; no sustituye estudios técnicos, permisos ni dictámenes.</span></div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
