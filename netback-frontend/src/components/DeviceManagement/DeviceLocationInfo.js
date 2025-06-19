import { Grid, FormControl, InputLabel, Select, MenuItem } from "@mui/material";

const DeviceLocationInfo = ({ formData, onChange, countries, sites, areas }) => (
  <Grid container spacing={2} sx={{ mt: 1 }}>
    <Grid item xs={6}>
      <FormControl fullWidth>
        <InputLabel>País</InputLabel>
        <Select name="country" value={formData.country} onChange={onChange} required>
          {countries.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={6}>
      <FormControl fullWidth>
        <InputLabel>Sitio</InputLabel>
        <Select name="site" value={formData.site} onChange={onChange} required>
          {sites.map((s) => <MenuItem key={s.id} value={s.id}>{s.name}</MenuItem>)}
        </Select>
      </FormControl>
    </Grid>
    <Grid item xs={12}>
      <FormControl fullWidth>
        <InputLabel>Área</InputLabel>
        <Select name="area" value={formData.area} onChange={onChange} required>
          {areas.map((a) => <MenuItem key={a.id} value={a.id}>{a.name}</MenuItem>)}
        </Select>
      </FormControl>
    </Grid>
  </Grid>
);

export default DeviceLocationInfo;
