function getStats(orderBy: string, orderDirection: string, searchTerm: string) {
  let base_url = "http://localhost:8000/stats/augments/list";
  const params: Record<string, string> = {
    order_by: orderBy,
    order_direction: orderDirection,
  };
  if (searchTerm) {
    params.search_term = searchTerm;
  }
  const query_string = new URLSearchParams(params).toString();
  const url = base_url + "?" + query_string;

  return fetch(url).then((response) => response.json());
}

export default getStats;
