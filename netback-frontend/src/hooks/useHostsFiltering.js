import { useMemo } from "react";

const useHostsFiltering = (hosts, searchTerm, page, rowsPerPage) => {
  const filteredHosts = useMemo(() =>
    hosts.filter((h) =>
      h.hostname.toLowerCase().includes(searchTerm.toLowerCase())
    ),
    [hosts, searchTerm]
  );

  const paginatedHosts = useMemo(() =>
    filteredHosts.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filteredHosts, page, rowsPerPage]
  );

  return { filteredHosts, paginatedHosts };
};

export default useHostsFiltering;
