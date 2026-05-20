### 1. Authentication & Headers
All requests to `https://public-api.etoro.com/api/v1/*` must include:
- `x-request-id`: A unique UUID for the request.
- `x-api-key`: Found in `ETORO_API_KEY` env var.
- `x-user-key`: Found in `ETORO_USER_API_KEY` env var (JWT).

### 2. Portfolio Retrieval
1.  Invoke the `etoro_get_portfolio_summary` (or direct GET request to `/api/v1/portfolio`).
2.  Parse the JSON response for:
    *   `Equity`: Total value.
    *   `NetProfit`: Current performance.
    *   `Positions`: List of holdings.

### 2. Trade Execution
1.  Validate the `symbol`, `direction` (Buy/Sell), and `amount` with the user.
2.  Invoke the `etoro_place_order` MCP tool.
3.  Report the `OrderID` and confirmation status.

## Error Handling
*   **Authentication Failure**: Prompt the user to re-verify their API key in the eToro Developer Portal.
*   **Rate Limiting**: Implement a retry strategy for 429 errors.
