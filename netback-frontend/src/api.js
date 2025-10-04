import axios from "axios";

//const API_URL = "http://netback-proxy:8080";
const API_URL = "/api";


//**********************************************************
// 🔐 Autenticación
//**********************************************************

// Login y almacenamiento del token
export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login/`, {
      username,
      password,
    });

    if (response.data.access) {
      const token = response.data.access;
      localStorage.setItem("token", token); // Guardar JWT

      // Obtener datos del usuario autenticado
      const me = await axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (me.data && me.data.role) {
        localStorage.setItem("role", me.data.role);
        localStorage.setItem("user", JSON.stringify(me.data));

      }
    }

    return response.data;
  } catch (error) {
    return null;
  }
};

// Logout
export const logout = () => {
  localStorage.removeItem("token");
};

//**********************************************************
// 👤 Gestión de usuarios
//**********************************************************

// Crear un nuevo usuario (Solo administradores)
export const createUser = async (data) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.post(`${API_URL}/users/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todos los usuarios
export const getUsers = async () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/users/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return [];
  }
};

// Obtener un usuario por ID (?)
export const getUserById = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/users/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Actualizar usuario (Admins pueden editar cualquier usuario, viewers solo el suyo)
export const updateUser = async (id, data) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.put(`${API_URL}/users/${id}/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar usuario (Solo administradores)
export const deleteUser = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.delete(`${API_URL}/users/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
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
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    const deviceData = {
      ...data,
      vault_credential: data.vault_credential || null, // Si no se usa Vault, enviar null
    };

    await axios.post(`${API_URL}/networkdevice/`, deviceData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todos los dispositivos
export const getDevices = async () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/networkdevice/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener un solo dispositivo por ID
export const getDeviceById = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/networkdevice/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Actualizar un dispositivo
export const updateDevice = async (id, data) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    const deviceData = {
      ...data
    };

    await axios.patch(`${API_URL}/networkdevice/${id}/`, deviceData, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar un dispositivo
export const deleteDevice = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.delete(`${API_URL}/networkdevice/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
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
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.post(`${API_URL}/vaultcredentials/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return true;
  } catch (error) {
    return false;
  }
};

// Obtener todas las credenciales Vault
export const getVaultCredentials = async () => {
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    const response = await axios.get(`${API_URL}/vaultcredentials/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

// Actualizar una credencial Vault
export const updateVaultCredential = async (id, data) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.put(`${API_URL}/vaultcredentials/${id}/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return true;
  } catch (error) {
    return false;
  }
};

// Eliminar una credencial Vault
export const deleteVaultCredential = async (id) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.delete(`${API_URL}/vaultcredentials/${id}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
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
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    const response = await axios.get(`${API_URL}/manufacturers/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

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
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    const response = await axios.get(`${API_URL}/devicetypes/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

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
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    const response = await axios.post(`${API_URL}/networkdevice/${deviceId}/backup/`, {}, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return false;
  }
};

// Obtener lista de dispositivos con su último respaldo
export const getLastBackups = async () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/backups_last/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener historial de respaldos de un dispositivo
export const getBackupHistory = async (deviceId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/networkdevice/${deviceId}/backups/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Ver contenido de un respaldo
export const getBackupDetails = async (backupId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/backup/${backupId}/`, {  // <-- Ruta corregida
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Comparar dos respaldos específicos por ID
export const compareSpecificBackups = async (backupOldId, backupNewId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/backups/compare/${backupOldId}/${backupNewId}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

// Comparar los dos últimos respaldos de un dispositivo
export const compareLastBackups = async (deviceId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/networkdevice/${deviceId}/compare/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};

//**********************************************************
// 🌍 Gestión de Países
//**********************************************************
export const createCountry = async (data) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    if (!data.name) {

      return null;
    }

    const response = await axios.post(`${API_URL}/countries/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data;
  } catch (error) {
    return null;
  }
};

export const getCountries = async () => {
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    const response = await axios.get(`${API_URL}/countries/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📍 Gestión de Sitios
//**********************************************************
export const createSite = async (data) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    if (!data.name || !data.country) {

      return null;
    }

    const response = await axios.post(`${API_URL}/sites/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return response.data;
  } catch (error) {
    return null;
  }
};

export const getSites = async (countryId = null) => {
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    let url = `${API_URL}/sites/`;
    if (countryId) url += `?country_id=${countryId}`;

    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

//**********************************************************
// 📍 Gestión de Áreas
//**********************************************************
export const getAreas = async (siteId = null, countryId = null) => {
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    let url = `${API_URL}/areas/`;
    if (siteId) url += `?site_id=${siteId}`;
    else if (countryId) url += `?country_id=${countryId}`;

    const response = await axios.get(url, {
      headers: { Authorization: `Bearer ${token}` },
    });

    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    return [];
  }
};

export const createArea = async (data) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    if (!data.name || !data.site) {

      return null;
    }

    const response = await axios.post(`${API_URL}/areas/`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });

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
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.post(
      `${API_URL}/backup-config/schedule/`,
      { scheduled_time: scheduledTime },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    return response.data;
  } catch (error) {
    return null;
  }
};

// Obtener el horario del respaldo
export const getBackupSchedule = async () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/backup-config/schedule/`, {
      headers: { Authorization: `Bearer ${token}` },
    });

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
  const token = localStorage.getItem("token");
  if (!token) return {
    success: false,
    message: "No hay token de autenticación"
  };

  try {
    const response = await axios.post(`${API_URL}/ping/`, { ip }, { 
      headers: { Authorization: `Bearer ${token}` },
    });

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
  const token = localStorage.getItem("token");
  if (!token) return [];

  try {
    const res = await axios.get(`${API_URL}/classification-rules/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  } catch (err) {
    return [];
  }
};

// Obtener un conjunto de reglas por ID
export const getClassificationRuleById = async (ruleSetId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const res = await axios.get(`${API_URL}/classification-rules/${ruleSetId}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
  } catch (err) {
    return null;
  }
};

// Clasificar hosts desde Zabbix
export const classifyFromZabbix = async (ruleSetId) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const res = await axios.post(
      `${API_URL}/networkdevice/bulk/from-zabbix/`,
      { ruleSetId },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
    return res.data;
  } catch (err) {
    return null;
  }
};

// Clasificar hosts desde CSV
export const classifyFromCSV = async (formData) => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const res = await axios.post(`${API_URL}/networkdevice/bulk/from-csv/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
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
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const res = await axios.post(`${API_URL}/networkdevice/bulk/save/`, payload, {
      headers: { Authorization: `Bearer ${token}` },
    });
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
  const token = localStorage.getItem("token");
  if (!token) return null;

  const url = ruleSetId
    ? `${API_URL}/classification-rules/${ruleSetId}/`
    : `${API_URL}/classification-rules/`;

  try {
    const response = ruleSetId
      ? await axios.put(url, data, { headers: { Authorization: `Bearer ${token}` } })
      : await axios.post(url, data, { headers: { Authorization: `Bearer ${token}` } });

    return response.data;
  } catch (error) {
    return null;
  }
};

// Eliminar conjunto de reglas
export const deleteClassificationRuleSet = async (ruleSetId) => {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    await axios.delete(`${API_URL}/classification-rules/${ruleSetId}/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return true;
  } catch (error) {
    return false;
  }
};


//**********************************************************
// 📡 Evaluacion conexion a zabbix
//**********************************************************
export const getZabbixStatus = async () => {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/zabbix/status/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    return null;
  }
};
