import apiClient from "./apiClient";
import { getAccessToken, setAccessToken, clearAuth } from "./auth";

//const API_URL = "http://netback-proxy:8080";
const API_URL = process.env.REACT_APP_API_URL || "/api";


//**********************************************************
// 🔐 Autenticación
//**********************************************************

// Login y almacenamiento del token
export const login = async (username, password) => {
  try {
    const response = await apiClient.post(`/auth/login/`, {
      username,
      password,
    });

    // backend should set refresh cookie (httpOnly) and return access in body
    if (response?.data?.access) {
      setAccessToken(response.data.access);

      // Obtener datos del usuario autenticado
      const me = await apiClient.get(`/users/me/`);

      if (me.data && me.data.role) {
        try {
          localStorage.setItem("role", me.data.role);
          localStorage.setItem("user", JSON.stringify(me.data));
        } catch (e) {
          // ignore storage errors
        }
      }
    }

    return response.data;
  } catch (error) {
    return null;
  }
};

// Logout: llamar al endpoint para que el backend/proxy borre las cookies,
// luego limpiar el estado local (in-memory + localStorage).
export const logout = async () => {
  try {
    // Intentar informar al servidor para que borre las cookies HttpOnly
    await apiClient.post(`/token/logout/`);
  } catch (e) {
    // Ignorar errores de red/servidor; proceder a limpiar el cliente igualmente
  }

  try {
    clearAuth();
    localStorage.removeItem("role");
    localStorage.removeItem("user");
  } catch (e) {
    // ignore
  }
};

//**********************************************************
// 👤 Gestión de usuarios
//**********************************************************

// Crear un nuevo usuario (Solo administradores)
export const createUser = async (data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.post(`/users/`, data);
    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todos los usuarios
export const getUsers = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/users/`);
    return response.data;
  } catch (error) {
    return [];
  }
};

// Obtener un usuario por ID (?)
export const getUserById = async (id) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/users/${id}/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

// Actualizar usuario (Admins pueden editar cualquier usuario, viewers solo el suyo)
export const updateUser = async (id, data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.put(`/users/${id}/`, data);
    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar usuario (Solo administradores)
export const deleteUser = async (id) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.delete(`/users/${id}/`);
    return true;
  } catch (error) {
    return false;
  }
};

//**********************************************************
// 🔌 Gestión de Dispositivos
//**********************************************************
// Crear un nuevo dispositivo
export const createDevice = async (data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    const deviceData = {
      ...data,
      vault_credential: data.vault_credential || null, // Si no se usa Vault, enviar null
    };

    await apiClient.post(`/networkdevice/`, deviceData);

    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todos los dispositivos
export const getDevices = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/networkdevice/`);

    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener un solo dispositivo por ID
export const getDeviceById = async (id) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/networkdevice/${id}/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

// Actualizar un dispositivo
export const updateDevice = async (id, data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    const deviceData = {
      ...data
    };

    await apiClient.patch(`/networkdevice/${id}/`, deviceData);

    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar un dispositivo
export const deleteDevice = async (id) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.delete(`/networkdevice/${id}/`);
    return true;
  } catch (error) {
    return false;
  }
};

//**********************************************************
// 🔑 Gestión de Credenciales Vault
//**********************************************************

// Crear una nueva credencial Vault
export const createVaultCredential = async (data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.post(`/vaultcredentials/`, data);
    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todas las credenciales Vault
export const getVaultCredentials = async () => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const response = await apiClient.get(`/vaultcredentials/`);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

// Actualizar una credencial Vault
export const updateVaultCredential = async (id, data) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.put(`/vaultcredentials/${id}/`, data);
    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar una credencial Vault
export const deleteVaultCredential = async (id) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.delete(`/vaultcredentials/${id}/`);
    return true;
  } catch (error) {
    return false;
  }
};

//**********************************************************
// 📍 Gestión de Fabricantes (Manufacturers)
//**********************************************************
// Obtener todas las marcas
export const getManufacturers = async () => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const response = await apiClient.get(`/manufacturers/`);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📍 Gestión de Tipos de Dispositivos (DeviceType)
//**********************************************************
// Obtener todos los tipos de dispositivos
export const getDeviceTypes = async () => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const response = await apiClient.get(`/devicetypes/`);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📂 Manejo de Respaldos
//**********************************************************

// Guardar un nuevo respaldo de un dispositivo
export const createBackup = async (deviceId) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    const response = await apiClient.post(`/networkdevice/${deviceId}/backup/`, {});
    return response.data;
  } catch (error) {
    return false;
  }
};

// Obtener lista de dispositivos con su último respaldo
export const getLastBackups = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/backups_last/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener historial de respaldos de un dispositivo
export const getBackupHistory = async (deviceId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/networkdevice/${deviceId}/backups/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

// Ver contenido de un respaldo
export const getBackupDetails = async (backupId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/backup/${backupId}/`);  // <-- Ruta corregida
    return response.data;
  } catch (error) {
    return null;
  }
};

// Comparar dos respaldos específicos por ID
export const compareSpecificBackups = async (backupOldId, backupNewId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/backups/compare/${backupOldId}/${backupNewId}/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

// Comparar los dos últimos respaldos de un dispositivo
export const compareLastBackups = async (deviceId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/networkdevice/${deviceId}/compare/`);
    return response.data;
  } catch (error) {
    return null;
  }
};

//**********************************************************
// 🌍 Gestión de Países
//**********************************************************
export const createCountry = async (data) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    if (!data.name) {

      return null;
    }

    const response = await apiClient.post(`/countries/`, data);

    return response.data;
  } catch (error) {
    return null;
  }
};

export const getCountries = async () => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const response = await apiClient.get(`/countries/`);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📍 Gestión de Sitios
//**********************************************************
export const createSite = async (data) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    if (!data.name || !data.country) {

      return null;
    }

    const response = await apiClient.post(`/sites/`, data);

    return response.data;
  } catch (error) {
    return null;
  }
};

export const getSites = async (countryId = null) => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    // Use relative path and params to avoid double /api when baseURL is set to /api
    const params = countryId ? { params: { country_id: countryId } } : {};
    const response = await apiClient.get(`/sites/`, params);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📍 Gestión de Áreas
//**********************************************************
export const getAreas = async (siteId = null, countryId = null) => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    // Use relative path and params to avoid double /api when baseURL is set to /api
    const params = siteId ? { params: { site_id: siteId } } : (countryId ? { params: { country_id: countryId } } : {});
    const response = await apiClient.get(`/areas/`, params);

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

export const createArea = async (data) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    if (!data.name || !data.site) {

      return null;
    }

    const response = await apiClient.post(`/areas/`, data);

    return response.data;
  } catch (error) {
    return null;
  }
};

//**********************************************************
// 📂 Gestión de Respaldo Automático
//**********************************************************
// Actualizar el horario del respaldo
export const updateBackupSchedule = async (scheduledTime) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.post(`/backup-config/schedule/`, { scheduled_time: scheduledTime });

    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener el horario del respaldo
export const getBackupSchedule = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/backup-config/schedule/`);

    return response.data;
  } catch (error) {
    return null;
  }
};

//**********************************************************
// 📡 Utilidades y Herramientas
//**********************************************************
// Hacer ping a un dispositivo antes de crearlo
export const pingDevice = async (ip) => {
  const token = getAccessToken();
  if (!token) return {
    success: false,
    message: "No hay token de autenticación"
  };

  try {
    const response = await apiClient.post(`/ping/`, { ip });

    // Si la respuesta es exitosa
    if (response.data.status === "success") {
      return {
        success: true,
        message: "✅ Dispositivo alcanzable"
      };
    }

    // Si hay un error, devolvemos la información detallada
    return {
      success: false,
      message: response.data.data?.message || response.data.message || "Error desconocido",
      details: response.data.data || {}
    };

  } catch (error) {
    // En caso de error de red o del servidor
    return {
      success: false,
      message: "❌ Error al realizar la prueba de conectividad",
      details: error.response?.data || {}
    };
  }
};

//**********************************************************
// Importacion de equipos
//**********************************************************

// Obtener todos los conjuntos de reglas
export const getClassificationRules = async () => {
  const token = getAccessToken();
  if (!token) return [];

  try {
    const res = await apiClient.get(`/classification-rules/`);
    return res.data;
  } catch (err) {
    return [];
  }
};

// Obtener un conjunto de reglas por ID
export const getClassificationRuleById = async (ruleSetId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const res = await apiClient.get(`/classification-rules/${ruleSetId}/`);
    return res.data;
  } catch (err) {
    return null;
  }
};

// Clasificar hosts desde Zabbix
export const classifyFromZabbix = async (ruleSetId) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const res = await apiClient.post(`/networkdevice/bulk/from-zabbix/`, { ruleSetId });
    return res.data;
  } catch (err) {
    return null;
  }
};

// Clasificar hosts desde CSV
export const classifyFromCSV = async (formData) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const res = await apiClient.post(`/networkdevice/bulk/from-csv/`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return res.data;
  } catch (err) {
    return null;
  }
};

// Guardar hosts clasificados seleccionados
export const saveClassifiedHosts = async (payload) => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const res = await apiClient.post(`/networkdevice/bulk/save/`, payload);
    return res.data;
  } catch (err) {
    return null;
  }
};


//**********************************************************
// 🧠 Gestión de Reglas de Clasificación
//**********************************************************

// Crear o actualizar conjunto de reglas
export const saveClassificationRuleSet = async (ruleSetId, data) => {
  const token = getAccessToken();
  if (!token) return null;

  const url = ruleSetId
    ? `/classification-rules/${ruleSetId}/`
    : `/classification-rules/`;

  try {
    const response = ruleSetId
      ? await apiClient.put(url, data)
      : await apiClient.post(url, data);

    return response.data;
  } catch (error) {
    return null;
  }
};

// Eliminar conjunto de reglas
export const deleteClassificationRuleSet = async (ruleSetId) => {
  const token = getAccessToken();
  if (!token) return false;

  try {
    await apiClient.delete(`/classification-rules/${ruleSetId}/`);
    return true;
  } catch (error) {
    return false;
  }
};


//**********************************************************
// 📡 Evaluacion conexion a zabbix
//**********************************************************
export const getZabbixStatus = async () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const response = await apiClient.get(`/zabbix/status/`);
    return response.data;
  } catch (error) {
    return null;
  }
};
