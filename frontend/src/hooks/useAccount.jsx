import React, { createContext, useContext, useEffect, useState } from "react";
import {
  accountError,
  enterAccount,
  ensureProfile,
  firebaseConfigured,
  leaveAccount,
  recordAnalysis,
  registerAccount,
  resetAccountPassword,
  savePlan,
  watchAccount,
  watchProfile,
} from "../services/firebase.mjs";

const EMPTY_USAGE = { usageMonth: "", analysisCount: 0 };
const AccountContext = createContext(null);

function useAccountState() {
  const configured = firebaseConfigured();
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [usage, setUsage] = useState(EMPTY_USAGE);
  const [authReady, setAuthReady] = useState(!configured);
  const [profileReady, setProfileReady] = useState(!configured);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(
    configured
      ? null
      : "Firebase no está configurado en este entorno. La vista muestra los planes, pero no puede guardar una cuenta.",
  );

  useEffect(() => {
    if (!configured) return undefined;
    let stopProfile = () => {};
    let cancelled = false;
    const stopAuth = watchAccount((next) => {
      stopProfile();
      stopProfile = () => {};
      setUser(next);
      setAuthReady(true);
      if (!next) {
        setRole(null);
        setUsage(EMPTY_USAGE);
        setProfileReady(true);
        setError(null);
        return;
      }
      // La sesión ya decide el acceso. El documento carga aparte, con
      // plan Básico por defecto, y su error no bloquea la entrada.
      setRole("basico");
      setUsage(EMPTY_USAGE);
      setProfileReady(false);
      ensureProfile(next).catch(() => {});
      stopProfile = watchProfile(
        next,
        (profile) => {
          if (cancelled) return;
          setRole(profile.role);
          setUsage({ usageMonth: profile.usageMonth, analysisCount: profile.analysisCount });
          setError(null);
          setProfileReady(true);
        },
        (cause) => {
          if (cancelled) return;
          setError(accountError(cause));
          setProfileReady(true);
        },
      );
    });
    return () => {
      cancelled = true;
      stopAuth();
      stopProfile();
    };
  }, [configured]);

  async function run(action) {
    setBusy(true);
    setError(null);
    try {
      return await action();
    } catch (cause) {
      setError(accountError(cause));
      return null;
    } finally {
      setBusy(false);
    }
  }

  function apply(profile) {
    setRole(profile.role);
    setUsage({ usageMonth: profile.usageMonth, analysisCount: profile.analysisCount });
    setProfileReady(true);
    return profile;
  }

  return {
    configured,
    user,
    role,
    usage,
    authReady,
    profileReady,
    // Compatibilidad: `ready` sigue disponible, pero ahora refleja la sesión.
    ready: authReady,
    busy,
    error,
    register(email, password, identity) {
      return run(async () => apply(await registerAccount(email, password, identity)));
    },
    enter(email, password, remember) {
      return run(async () => apply(await enterAccount(email, password, remember)));
    },
    resetPassword(email) {
      return run(() => resetAccountPassword(email));
    },
    choose(planId) {
      return run(async () => {
        const next = await savePlan(user, planId);
        setRole(next);
        return next;
      });
    },
    consume() {
      return run(async () => {
        const next = await recordAnalysis(user);
        setUsage(next);
        return next;
      });
    },
    leave() {
      return run(() => leaveAccount());
    },
  };
}

export function AccountProvider({ children }) {
  const account = useAccountState();
  return <AccountContext.Provider value={account}>{children}</AccountContext.Provider>;
}

export function useAccount() {
  const account = useContext(AccountContext);
  if (!account) {
    throw new Error("useAccount debe usarse dentro de AccountProvider.");
  }
  return account;
}
