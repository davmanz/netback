import { Grid, TextField, FormControl, InputLabel, Select, MenuItem } from "@mui/material";

const DeviceHardwareInfo = ({ formData, onChange, manufacturers, deviceTypes }) => (
  <Grid container spacing={2} sx={{ mt: 1 }}>
    <Grid item xs={6}>
      <FormControl fullWidth>
        <InputLabel>Fabricante</InputLabel>
        <Select name="manufacturer" value={formData.manufacturer} onChange={onChange} required>
          {manufacturers.map((m) => <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>)}
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={6}>
      <FormControl fullWidth>
        <InputLabel>Tipo de Dispositivo</InputLabel>
        <Select name="deviceType" value={formData.deviceType} onChange={onChange} required>
          {deviceTypes.map((d) => <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>)}
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={12}>
      <TextField fullWidth label="Modelo" name="model" value={formData.model} onChange={onChange} required />
    </Grid>
  </Grid>
);

export default DeviceHardwareInfo;
