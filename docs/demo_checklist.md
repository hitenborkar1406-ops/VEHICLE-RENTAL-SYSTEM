# Demonstration Checklist — Vehicle Rental System

Use this checklist during your college evaluation demo or for manual testing.

---

## Pre-Demo Setup

- [ ] Open terminal in `Vehicle Rental System` directory
- [ ] Run `pip install -r requirements.txt` (if not done)
- [ ] Run `python run.py`
- [ ] Verify application loads at http://127.0.0.1:5000
- [ ] Open a browser to the dashboard

---

## 1. Dashboard

- [ ] Dashboard loads with statistics (seeded luxury fleet & active bookings)
- [ ] Vehicle stats show: Total, Available, Rented, Maintenance
- [ ] Booking stats show: Total, Active, Cancelled, Completed
- [ ] Revenue summary displays calculated active booking earnings
- [ ] Navigation links work (Dashboard, Vehicles, Bookings)
- [ ] "Add Vehicle" and "New Booking" buttons work

---

## 2. Vehicle Management

### 2.1 Add Vehicles

- [ ] Navigate to Vehicles → Add Vehicle
- [ ] Add Vehicle 1:
  - Registration: `MH-01-AB-1234`
  - Name: `Toyota Innova Crysta`
  - Type: `Car`
  - Daily Rate: `2500`
  - ✅ Success message shown
- [ ] Add Vehicle 2:
  - Registration: `KA-05-XY-9876`
  - Name: `Mahindra Thar`
  - Type: `SUV`
  - Daily Rate: `3500`
  - ✅ Success message shown
- [ ] Add Vehicle 3:
  - Registration: `DL-10-CD-5678`
  - Name: `Honda Activa`
  - Type: `Motorcycle`
  - Daily Rate: `500`
  - ✅ Success message shown

### 2.2 Validation Errors

- [ ] Try submitting empty form → All required field errors shown
- [ ] Try duplicate registration `MH-01-AB-1234` → "already exists" error
- [ ] Try rate = `0` → "positive number" error
- [ ] Try rate = `-100` → "positive number" error
- [ ] Try invalid type → "must be one of" error

### 2.3 Search and Filter

- [ ] Search for "Toyota" → Only Toyota shown
- [ ] Search for "KA-05" → Only Mahindra Thar shown
- [ ] Filter by Type = SUV → Only Thar shown
- [ ] Filter by Status = Available → All shown (default status)
- [ ] Clear filters → All vehicles shown

### 2.4 Edit Vehicle

- [ ] Click Edit on any vehicle
- [ ] Change the name and rate
- [ ] Submit → "updated successfully" message
- [ ] Verify changes in the list

### 2.5 Delete Vehicle (No Bookings)

- [ ] Add a temporary vehicle (e.g., `TEST-DELETE-001`)
- [ ] Delete it → "deleted successfully" message
- [ ] Vehicle no longer in list

---

## 3. Booking Management

### 3.1 Create Booking

- [ ] Navigate to Bookings → New Booking
- [ ] Select `Toyota Innova Crysta`
- [ ] Enter customer: `Rajesh Kumar`
- [ ] Start date: Tomorrow's date
- [ ] End date: 3 days from tomorrow
- [ ] Observe rental preview (client-side estimate)
- [ ] Submit → "Booking created successfully" with calculation details
- [ ] Verify 3 days × ₹2500 = ₹7500 (inclusive calculation)

### 3.2 Booking Validation

- [ ] Try empty form → Required field errors
- [ ] Try end date before start date → Date range error
- [ ] Try past dates → "cannot be in the past" error

### 3.3 Overlapping Booking

- [ ] Try booking same vehicle for overlapping dates → "already has an active booking" error
- [ ] Try booking same vehicle for adjacent (non-overlapping) dates → Success

### 3.4 View Booking

- [ ] Click "View" on the created booking
- [ ] Verify: vehicle info, customer, dates, days, amount, status
- [ ] Verify rental calculation breakdown shown

### 3.5 Cancel Booking

- [ ] Click "Cancel" on the active booking
- [ ] Confirm the cancellation prompt
- [ ] ✅ "Booking cancelled successfully" message
- [ ] Status badge shows "Cancelled"
- [ ] Try cancelling again → "Only active bookings" error

### 3.6 Rebook After Cancellation

- [ ] Create a new booking for the same vehicle and same dates
- [ ] ✅ Booking created successfully (cancelled booking released dates)

### 3.7 Delete Vehicle with Bookings

- [ ] Try to delete Toyota Innova Crysta (has booking history)
- [ ] ❌ "Cannot delete" error — booking history preserved

---

## 4. Dashboard (After Data Entry)

- [ ] Return to Dashboard
- [ ] Vehicle stats updated (3 total, available/rented/maintenance counts)
- [ ] Booking stats updated (active, cancelled counts)
- [ ] Revenue reflects active bookings
- [ ] Recent bookings table shows entries

---

## 5. Responsive Design

- [ ] Resize browser to mobile width
- [ ] Hamburger menu appears and works
- [ ] Tables scroll horizontally
- [ ] Forms stack vertically
- [ ] Stat cards reflow

---

## 6. Run Automated Tests

```bash
python -m pytest -v
```

- [ ] All 47 tests pass
- [ ] No errors or warnings
- [ ] Tests complete in < 5 seconds

---

## Post-Demo Cleanup

- [ ] Stop the server (Ctrl+C in terminal)
- [ ] Optionally delete `instance/vehicle_rental.db` to reset data
- [ ] The database and sample luxury fleet are recreated automatically on next startup

---

## Common Issues and Fixes

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Run `pip install -r requirements.txt` |
| Port 5000 already in use | Change port in `run.py` or kill the other process |
| Database locked error | Stop other instances of the application |
| Tests fail with import errors | Run tests from the project root directory |
