import { useEffect, useState, useMemo } from "react";
import {
  getSites, createSite, getAreas, createArea, getCountries,
} from "../api";
import {
  Box, Typography, Accordion, AccordionSummary, AccordionDetails, Button,
  Snackbar, Alert, CircularProgress,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import SiteDialog from "./modals/SiteAndAreas/SiteDialog";
import AreaDialog from "./modals/SiteAndAreas/AreaDialog";

const SitesAndAreas = () => {
  const [countries, setCountries] = useState([]);
  const [sites, setSites] = useState([]);
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);

  const [newSite, setNewSite] = useState({ name: "", country: "" });
  const [newArea, setNewArea] = useState({ name: "", site: "" });

  const [openSiteDialog, setOpenSiteDialog] = useState(false);
  const [openAreaDialog, setOpenAreaDialog] = useState(false);
  const [areaContextSite, setAreaContextSite] = useState(null);

  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "info" });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [countryList, siteList, areaList] = await Promise.all([
        getCountries(),
        getSites(),
        getAreas(),
      ]);
      setCountries(countryList);
      setSites(siteList);
      setAreas(areaList);
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Error al cargar datos: ${error.message}`,
        severity: "error",
      });
    }
    setLoading(false);
  };

  const validateSite = (site) => {
    const errors = {};
    if (!site.name.trim()) errors.name = "El nombre es requerido";
    if (!site.country) errors.country = "El país es requerido";
    return errors;
  };

  const validateArea = (area) => {
    const errors = {};
    if (!area.name.trim()) errors.name = "El nombre es requerido";
    if (!area.site) errors.site = "El sitio es requerido";
    return errors;
  };

  const handleCreateSite = async () => {
    const errors = validateSite(newSite);
    if (Object.keys(errors).length > 0) {
      setSnackbar({ open: true, message: "Completa todos los campos del Site", severity: "error" });
      return;
    }
    const res = await createSite(newSite);
    if (res) {
      await fetchData();
      setSnackbar({ open: true, message: "Site creado con éxito", severity: "success" });
      setOpenSiteDialog(false);
      setNewSite({ name: "", country: "" });
    }
  };

  const handleCreateArea = async () => {
  const siteId = newArea.site || areaContextSite;

  const errors = validateArea({ ...newArea, site: siteId });
    if (Object.keys(errors).length > 0) {
      setSnackbar({ open: true, message: "Completa todos los campos del Área", severity: "error" });
      return;
    }

    const res = await createArea({ ...newArea, site: siteId });
    if (res) {
      await fetchData();
      setSnackbar({ open: true, message: "Área creada con éxito", severity: "success" });
      setOpenAreaDialog(false);
      setNewArea({ name: "", site: "" });
    }
  };


  const groupedByCountry = useMemo(() => {
    return countries.reduce((acc, country) => {
      acc[country.id] = {
        ...country,
        sites: sites.filter((s) => s.country === country.id),
      };
      return acc;
    }, {});
  }, [countries, sites]);

  const areasBySite = useMemo(() => {
    return areas.reduce((acc, area) => {
      if (!acc[area.site]) acc[area.site] = [];
      acc[area.site].push(area);
      return acc;
    }, {});
  }, [areas]);

  return (
    <Box sx={{
      p: { xs: 2, sm: 3, md: 4 },
      width: "100%",
      maxWidth: { xs: '100%', md: 900 },
      mx: "auto"
    }}>
      <Typography variant="h4" gutterBottom>Gestión de Sites y Áreas</Typography>

      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={() => setOpenSiteDialog(true)}>
          ➕ Crear Site
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ textAlign: "center", py: 5 }}>
          <CircularProgress />
        </Box>
      ) : (
        Object.values(groupedByCountry).map((country) => (
          <Accordion key={country.id}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography fontWeight="bold">🌍 {country.name}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              {country.sites.length === 0 ? (
                <Typography sx={{ ml: 2 }}>No hay Sites registrados</Typography>
              ) : (
                country.sites.map((site) => (
                  <Accordion key={site.id} sx={{ ml: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography>🏢 {site.name}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ mb: 1 }}>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            setAreaContextSite(site.id);
                            setNewArea({ name: "", site: site.id });
                            setOpenAreaDialog(true);
                          }}
                        >
                          ➕ Agregar Área
                        </Button>
                      </Box>
                      {areasBySite[site.id]?.length > 0 ? (
                        areasBySite[site.id].map((a) => (
                          <Typography key={a.id} sx={{ ml: 2 }}>▪️ {a.name}</Typography>
                        ))
                      ) : (
                        <Typography sx={{ ml: 2 }}>No hay Áreas</Typography>
                      )}
                    </AccordionDetails>
                  </Accordion>
                ))
              )}
            </AccordionDetails>
          </Accordion>
        ))
      )}

      {/* Dialogs reutilizables */}
      <SiteDialog
        open={openSiteDialog}
        onClose={() => setOpenSiteDialog(false)}
        newSite={newSite}
        setNewSite={setNewSite}
        onSave={handleCreateSite}
        countries={countries}
      />

      <AreaDialog
        open={openAreaDialog}
        onClose={() => setOpenAreaDialog(false)}
        newArea={newArea}
        setNewArea={setNewArea}
        onSave={handleCreateArea}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default SitesAndAreas;
