import { Grid, TextField } from "@mui/material";

const DeviceBasicInfo = ({ formData, onChange }) => (
  <Grid container spacing={2} sx={{ mt: 1 }}>
    <Grid item xs={6}>
      <TextField fullWidth label="Hostname" name="hostname" value={formData.hostname} onChange={onChange} required />
    </Grid>
    <Grid item xs={6}>
      <TextField fullWidth label="IP Address" name="ipAddress" value={formData.ipAddress} onChange={onChange} required />
    </Grid>
  </Grid>
);

export default DeviceBasicInfo;
