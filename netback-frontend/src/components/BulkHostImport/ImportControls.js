import React from "react";
import { Box, Button } from "@mui/material";
import { useZabbixStore } from "../../store/zabbixStore";
  

const ImportControls = ({
  onZabbixImport,
  onFileChange,
  onCSVImport,
  loading,
  selectedRule,
  file
}) => {
  const isZabbixAvailable = useZabbixStore((state) => state.isZabbixAvailable());
  return (
    
    <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
      {isZabbixAvailable && (
      <Button variant="contained" onClick={onZabbixImport} disabled={loading || !selectedRule}>
        Clasificar desde Zabbix
      </Button>
    )}

      <Button variant="contained" component="label">
        Subir CSV
        <input type="file" accept=".csv" hidden onChange={onFileChange} />
      </Button>

      <Button variant="contained" onClick={onCSVImport} disabled={loading || !file || !selectedRule}>
        Clasificar desde CSV
      </Button>
    </Box>
  );
};

export default React.memo(ImportControls);
