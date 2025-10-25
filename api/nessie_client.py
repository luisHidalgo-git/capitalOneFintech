import requests
from typing import Dict, List, Optional, Any
from config import NESSIE_API_KEY, NESSIE_BASE_URL

class NessieAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")

class NessieClient:
    def __init__(self):
        self.base_url = NESSIE_BASE_URL
        self.api_key = NESSIE_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code in [200, 201]:
                return response.json() if response.text else None
            elif response.status_code == 404:
                raise NessieAPIError(404, "Resource not found")
            elif response.status_code == 400:
                raise NessieAPIError(400, "Bad request")
            else:
                raise NessieAPIError(response.status_code, response.text)

        except requests.exceptions.RequestException as e:
            raise NessieAPIError(500, f"Connection error: {str(e)}")

    def get_customers(self) -> List[Dict]:
        return self._make_request("GET", "/customers")

    def get_customer(self, customer_id: str) -> Dict:
        return self._make_request("GET", f"/customers/{customer_id}")

    def create_customer(self, first_name: str, last_name: str, address: Dict) -> Dict:
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address
        }
        return self._make_request("POST", "/customers", data)

    def update_customer(self, customer_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/customers/{customer_id}", data)

    def delete_customer(self, customer_id: str) -> None:
        return self._make_request("DELETE", f"/customers/{customer_id}")

    def get_accounts(self) -> List[Dict]:
        return self._make_request("GET", "/accounts")

    def get_account(self, account_id: str) -> Dict:
        return self._make_request("GET", f"/accounts/{account_id}")

    def create_account(self, account_type: str, nickname: str, rewards: int = 0,
                      balance: float = 0, account_number: Optional[str] = None) -> Dict:
        data = {
            "type": account_type,
            "nickname": nickname,
            "rewards": rewards,
            "balance": balance
        }
        if account_number:
            data["account_number"] = account_number
        return self._make_request("POST", "/accounts", data)

    def update_account(self, account_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/accounts/{account_id}", data)

    def delete_account(self, account_id: str) -> None:
        return self._make_request("DELETE", f"/accounts/{account_id}")

    def get_account_customer(self, account_id: str) -> Dict:
        return self._make_request("GET", f"/accounts/{account_id}/customer")

    def get_account_transfers(self, account_id: str) -> List[Dict]:
        return self._make_request("GET", f"/accounts/{account_id}/transfers")

    def get_transfer(self, transfer_id: str) -> Dict:
        return self._make_request("GET", f"/transfers/{transfer_id}")

    def create_transfer(self, account_id: str, medium: str, payee_id: str,
                       amount: float, transaction_date: str,
                       description: Optional[str] = None) -> Dict:
        data = {
            "medium": medium,
            "payee_id": payee_id,
            "amount": amount,
            "transaction_date": transaction_date
        }
        if description:
            data["description"] = description
        return self._make_request("POST", f"/accounts/{account_id}/transfers", data)

    def update_transfer(self, transfer_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/transfers/{transfer_id}", data)

    def delete_transfer(self, transfer_id: str) -> None:
        return self._make_request("DELETE", f"/transfers/{transfer_id}")

    def get_account_bills(self, account_id: str) -> List[Dict]:
        return self._make_request("GET", f"/accounts/{account_id}/bills")

    def get_bill(self, bill_id: str) -> Dict:
        return self._make_request("GET", f"/bills/{bill_id}")

    def create_bill(self, account_id: str, status: str, payee: str,
                   nickname: str, payment_date: str,
                   recurring_date: Optional[int] = None,
                   payment_amount: Optional[float] = None) -> Dict:
        data = {
            "status": status,
            "payee": payee,
            "nickname": nickname,
            "payment_date": payment_date
        }
        if recurring_date is not None:
            data["recurring_date"] = recurring_date
        if payment_amount is not None:
            data["payment_amount"] = payment_amount
        return self._make_request("POST", f"/accounts/{account_id}/bills", data)

    def update_bill(self, bill_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/bills/{bill_id}", data)

    def delete_bill(self, bill_id: str) -> None:
        return self._make_request("DELETE", f"/bills/{bill_id}")

    def get_account_deposits(self, account_id: str) -> List[Dict]:
        return self._make_request("GET", f"/accounts/{account_id}/deposits")

    def get_deposit(self, deposit_id: str) -> Dict:
        return self._make_request("GET", f"/deposits/{deposit_id}")

    def create_deposit(self, account_id: str, medium: str, amount: float,
                      transaction_date: str, description: Optional[str] = None) -> Dict:
        data = {
            "medium": medium,
            "amount": amount,
            "transaction_date": transaction_date
        }
        if description:
            data["description"] = description
        return self._make_request("POST", f"/accounts/{account_id}/deposits", data)

    def update_deposit(self, deposit_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/deposits/{deposit_id}", data)

    def delete_deposit(self, deposit_id: str) -> None:
        return self._make_request("DELETE", f"/deposits/{deposit_id}")

    def get_account_withdrawals(self, account_id: str) -> List[Dict]:
        return self._make_request("GET", f"/accounts/{account_id}/withdrawals")

    def get_withdrawal(self, withdrawal_id: str) -> Dict:
        return self._make_request("GET", f"/withdrawals/{withdrawal_id}")

    def create_withdrawal(self, account_id: str, medium: str, amount: float,
                         transaction_date: str, description: Optional[str] = None) -> Dict:
        data = {
            "medium": medium,
            "amount": amount,
            "transaction_date": transaction_date
        }
        if description:
            data["description"] = description
        return self._make_request("POST", f"/accounts/{account_id}/withdrawals", data)

    def update_withdrawal(self, withdrawal_id: str, data: Dict) -> Dict:
        return self._make_request("PUT", f"/withdrawals/{withdrawal_id}", data)

    def delete_withdrawal(self, withdrawal_id: str) -> None:
        return self._make_request("DELETE", f"/withdrawals/{withdrawal_id}")
