import { useState, useEffect } from "react";
import { getDevices, getLastBackups } from "../api";

export const useDevices = () => {
  const [devices, setDevices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDevices = async () => {
    try {
      setIsLoading(true);
      const devicesData = await getDevices();
      const backupsData = await getLastBackups();

      if (devicesData && backupsData) {
        const mergedDevices = devicesData.map((device) => {
          const backup = backupsData.find((b) => b.id === device.id);
          return {
            ...device,
            backup_id: backup?.backup_id ?? null,
            last_updated: backup?.lastBackup ?? "No disponible",
          };
        });
        setDevices(mergedDevices);
      }
    } catch (err) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  return { devices, isLoading, error, loadDevices };
};
