import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import { getAccessToken } from './auth';
import Dashboard from "./pages/Dashboard";
import DeviceManagement from "./pages/DeviceManagement";
import Layout from "./pages/Layout";
import Users from "./pages/Users";
import Backups from "./pages/Backups";
import CompareBackups from "./pages/CompareBackups";
import SitesAndAreas from "./pages/SitesAndAreas";
import VaultCredentials from "./pages/VaultCredentials";
import BackupSchedule from "./pages/BackupSchedule"; 
import BulkHostImport from "./pages/BulkHostImport";
import ClassificationRules from "./pages/ClassificationRules";
import ZabbixStatus from "./pages/ZabbixStatus";


const PrivateRoute = ({ children }) => {
  const token = getAccessToken();
  return token ? children : <Navigate to="/" />;
};


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        
        <Route path="/dashboard" element={
          <PrivateRoute>
            <Layout>
              <Dashboard />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/users" element={
          <PrivateRoute>
            <Layout>
              <Users />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/manage-devices" element={
          <PrivateRoute>
            <Layout>
              <DeviceManagement />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/backups" element={
          <PrivateRoute>
            <Layout>
              <Backups />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/compare-backups" element={
          <PrivateRoute>
            <Layout>
              <CompareBackups />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/sites-and-areas" element={
          <PrivateRoute>
            <Layout>
              <SitesAndAreas />
            </Layout>
          </PrivateRoute>
        } />

        <Route path="/backup/:deviceId/history" element={
          <PrivateRoute>
            <Layout>
              <Backups />
            </Layout>
          </PrivateRoute>
        } />
        
        <Route path="/vault-credentials" element={
          <PrivateRoute>
            <Layout>
              <VaultCredentials />
            </Layout>
          </PrivateRoute>
        } />

        <Route path="/backup-schedule" element={
          <PrivateRoute>
            <Layout>
              <BackupSchedule />
            </Layout>
          </PrivateRoute>
        } />

        <Route path="/classification-rules" element={
          <PrivateRoute>
            <Layout>
              <ClassificationRules />
            </Layout>
          </PrivateRoute>
        } />

        <Route path="/bulk-import" element={
          <PrivateRoute>
            <Layout>
              <BulkHostImport />
            </Layout>
          </PrivateRoute>
        } />

        <Route path="/zabbix-status" element={
          <PrivateRoute>
            <Layout>
              <ZabbixStatus />
            </Layout>
          </PrivateRoute>
        } />
      </Routes>
    </Router>
  );
}

export default App;
