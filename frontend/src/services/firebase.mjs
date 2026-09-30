import { initializeApp } from "firebase/app";
import {
  browserLocalPersistence,
  browserSessionPersistence,
  createUserWithEmailAndPassword,
  getAuth,
  onAuthStateChanged,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import {
  doc,
  getDoc,
  getFirestore,
  onSnapshot,
  serverTimestamp,
  setDoc,
} from "firebase/firestore";
import { PLAN_IDS, analysisLimit, isKnownPlan, usageMonth } from "../plans.mjs";

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

let services;

export function firebaseConfigured() {
  return Boolean(config.apiKey && config.authDomain && config.projectId && config.appId);
}

function client() {
  if (!firebaseConfigured()) {
    throw new Error("Firebase no está configurado en este entorno.");
  }
  if (!services) {
    const app = initializeApp(config);
    const auth = getAuth(app);
    auth.languageCode = "es";
    services = { auth, db: getFirestore(app) };
  }
  return services;
}

export function watchAccount(onChange) {
  const { auth } = client();
  return onAuthStateChanged(auth, onChange);
}

export async function getAccountToken() {
  if (!firebaseConfigured()) return null;
  const { auth } = client();
  await auth.authStateReady();
  return auth.currentUser ? auth.currentUser.getIdToken() : null;
}

function readUsage(data) {
  return {
    usageMonth: typeof data?.usageMonth === "string" ? data.usageMonth : "",
    analysisCount: Number.isInteger(data?.analysisCount) ? data.analysisCount : 0,
  };
}

function storedPlan(data) {
  if (isKnownPlan(data?.plan)) return data.plan;
  if (isKnownPlan(data?.role)) return data.role;
  return null;
}

function profileFrom(data) {
  return {
    role: storedPlan(data) || "basico",
    fullName: typeof data?.fullName === "string" ? data.fullName : "",
    institution: typeof data?.institution === "string" ? data.institution : "",
    ...readUsage(data),
  };
}

function userRecord(user, plan, creating) {
  return {
    email: user.email || "",
    plan,
    role: plan,
    updatedAt: serverTimestamp(),
    ...(creating ? { createdAt: serverTimestamp() } : {}),
  };
}

export async function ensureProfile(user) {
  const { db } = client();
  await user.getIdToken();
  const ref = doc(db, "users", user.uid);
  const snap = await getDoc(ref);
  const current = snap.exists() ? storedPlan(snap.data()) : null;
  if (current) return profileFrom(snap.data());
  await setDoc(ref, userRecord(user, "basico", true));
  return { role: "basico", usageMonth: "", analysisCount: 0 };
}

export function watchProfile(user, onProfile, onError) {
  const { db } = client();
  const ref = doc(db, "users", user.uid);
  // Solo observa. La creación del documento la hace ensureProfile en el
  // proveedor, así que aquí no se escribe para no duplicar el alta.
  return onSnapshot(
    ref,
    (snap) => {
      const plan = snap.exists() ? storedPlan(snap.data()) : null;
      if (plan) {
        onProfile(profileFrom(snap.data()));
        return;
      }
      onProfile({ role: "basico", usageMonth: "", analysisCount: 0 });
    },
    onError,
  );
}

const DEFAULT_PROFILE = { role: "basico", usageMonth: "", analysisCount: 0 };

export async function registerAccount(email, password, identity = {}) {
  const { auth, db } = client();
  const credential = await createUserWithEmailAndPassword(auth, email, password);
  const fullName = (identity.fullName || "").trim();
  const institution = (identity.institution || "").trim();
  // El documento no debe frenar el ingreso. Si Firestore no responde, se
  // entra con plan Básico y el alta se completa después.
  let profile = { ...DEFAULT_PROFILE };
  try {
    profile = await ensureProfile(credential.user);
    if (fullName || institution) {
      await setDoc(
        doc(db, "users", credential.user.uid),
        {
          ...(fullName ? { fullName } : {}),
          ...(institution ? { institution } : {}),
          updatedAt: serverTimestamp(),
        },
        { merge: true },
      );
    }
  } catch {
    // La sesión ya existe; el perfil se sincroniza cuando Firestore esté listo.
  }
  return { user: credential.user, ...profile, fullName, institution };
}

export async function enterAccount(email, password, remember = true) {
  const { auth } = client();
  await setPersistence(auth, remember ? browserLocalPersistence : browserSessionPersistence);
  const credential = await signInWithEmailAndPassword(auth, email, password);
  let profile = { ...DEFAULT_PROFILE };
  try {
    profile = await ensureProfile(credential.user);
  } catch {
    // Entra igual; el documento se carga aparte.
  }
  return { user: credential.user, ...profile };
}

export async function resetAccountPassword(email) {
  const { auth } = client();
  await sendPasswordResetEmail(auth, email);
  return true;
}

export async function savePlan(user, plan) {
  if (!user?.uid) throw new Error("Entra con tu cuenta antes de elegir un plan.");
  if (!PLAN_IDS.includes(plan)) throw new Error("Ese plan no existe.");
  await ensureProfile(user);
  const { db } = client();
  await setDoc(doc(db, "users", user.uid), userRecord(user, plan, false), { merge: true });
  return plan;
}

export async function recordAnalysis(user) {
  const { db } = client();
  const ref = doc(db, "users", user.uid);
  const snap = await getDoc(ref);
  const stored = readUsage(snap.data());
  const month = usageMonth();
  const limit = analysisLimit(storedPlan(snap.data()) || "basico");
  const count = stored.usageMonth === month ? stored.analysisCount : 0;
  const next = {
    usageMonth: month,
    analysisCount: limit == null ? count : Math.min(count + 1, limit),
  };
  await setDoc(ref, { ...next, updatedAt: serverTimestamp() }, { merge: true });
  return next;
}

export async function leaveAccount() {
  const { auth } = client();
  await signOut(auth);
}

const AUTH_ERRORS = {
  "auth/invalid-email": "El correo no tiene un formato válido.",
  "auth/missing-password": "Escribe una contraseña.",
  "auth/weak-password": "La contraseña debe tener al menos 6 caracteres.",
  "auth/email-already-in-use": "Ese correo ya tiene una cuenta. Entra con él.",
  "auth/invalid-credential": "Correo o contraseña incorrectos.",
  "auth/user-not-found": "No hay una cuenta con ese correo.",
  "auth/wrong-password": "Correo o contraseña incorrectos.",
  "auth/too-many-requests": "Demasiados intentos. Espera un momento y vuelve a intentar.",
  "auth/network-request-failed": "No hay conexión con Firebase. Revisa la red.",
  "auth/operation-not-allowed":
    "El acceso por correo todavía no está activado en la consola de Firebase.",
  "auth/configuration-not-found":
    "En Firebase falta activar Authentication con correo y contraseña.",
  "permission-denied":
    "Firestore rechazó el documento del usuario. Crea la base y publica las reglas de firestore.rules.",
  "failed-precondition":
    "En Firebase falta crear la base de datos Firestore.",
  "not-found": "No existe la base de Firestore de este proyecto.",
};

export function accountError(error) {
  if (AUTH_ERRORS[error?.code]) return AUTH_ERRORS[error.code];
  if (!error?.code && error?.message) return error.message;
  return "No se pudo completar la operación con Firebase.";
}
