import { create } from "zustand";

// Zustand Store para el estado de Zabbix
export const useZabbixStore = create((set, get) => ({
  zabbixStatus: null,

  // Función para actualizar el estado
  setZabbixStatus: (status) => set({ zabbixStatus: status }),

  // Getter computado para saber si Zabbix está disponible
  isZabbixAvailable: () => {
    const status = get().zabbixStatus;
    return status?.activate === true && status?.zabbix_api_status === "ok";
  },
}));
