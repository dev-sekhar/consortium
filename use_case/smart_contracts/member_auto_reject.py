from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, TYPE_CHECKING
from enum import Enum

import json
import threading
import time
from utilities.notification import send_reminder

if TYPE_CHECKING:
    from core.membership import Membership


class TimeUnit(Enum):
    """Supported time units for configuration"""
    MINUTES = "minutes"
    HOURS = "hours"


class MemberAutoRejectContract:
    """
    Smart contract that handles automatic rejection of membership requests after a specified time period.
    Includes reminder functionality to notify lenders before auto-rejection occurs.
    """

    def __init__(self, membership: 'Membership') -> None:
        """
        Initialize the auto-reject contract.

        Args:
            membership: Reference to the Membership class instance
                       Used to access member data and voting functions
        """
        self.membership = membership
        self.config_file = 'use_case/config/timing_config.json'

        # Load timing configuration from JSON file
        with open(self.config_file, 'r') as file:
            config = json.load(file)
            self.config = config['membership']['request']['auto_reject']

        # Validate time units
        self._validate_time_units(self.config)

        # Start monitoring thread only if auto-reject feature is enabled
        if self.config['enabled']:
            self._start_monitoring()

    def _validate_time_units(self, config: Dict[str, Any]) -> None:
        """
        Validate that time units in configuration are supported.

        Args:
            config: Configuration dictionary containing time settings

        Raises:
            ValueError: If an unsupported time unit is found
        """
        valid_units = {unit.value for unit in TimeUnit}

        for timing in ['timeout', 'reminder']:
            unit = config[timing]['unit']
            if unit not in valid_units:
                raise ValueError(f"Unsupported time unit '{
                                 unit}'. Must be one of: {valid_units}")

    def _convert_to_timedelta(self, value: int, unit: str) -> timedelta:
        """
        Convert a time value and unit to a timedelta object.

        Args:
            value: Number of time units
            unit: Unit of time ('minutes' or 'hours')

        Returns:
            timedelta object representing the specified time
        """
        if unit == TimeUnit.MINUTES.value:
            return timedelta(minutes=value)
        elif unit == TimeUnit.HOURS.value:
            return timedelta(hours=value)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")

    def _start_monitoring(self) -> None:
        """
        Start a daemon thread to monitor pending membership requests.
        Thread runs in background and doesn't prevent program from exiting.
        """
        self.monitor_thread = threading.Thread(
            target=self._monitor_requests,
            daemon=True
        )
        self.monitor_thread.start()

    def _monitor_requests(self) -> None:
        """
        Continuously monitor pending requests for timing conditions.
        """
        print("Starting monitoring thread...")  # Initial startup message

        while True:
            try:
                if not self.config['enabled']:
                    print("Auto-reject disabled, stopping monitoring thread")
                    break

                current_time = datetime.utcnow()
                pending_requests = self.membership.get_pending_requests()

                # Only log if there are pending requests
                if pending_requests:
                    print(f"Checking {len(pending_requests)
                                      } pending requests at {current_time}")

                for request in pending_requests:
                    # Convert Unix timestamp to string for fromisoformat
                    request_time_str = datetime.fromtimestamp(
                        request['timestamp']).isoformat()
                    request_time = datetime.fromisoformat(request_time_str)

                    # Calculate timing thresholds
                    auto_reject_time = request_time + self._convert_to_timedelta(
                        self.config['timeout']['value'],
                        self.config['timeout']['unit']
                    )
                    reminder_time = auto_reject_time - self._convert_to_timedelta(
                        self.config['reminder']['value'],
                        self.config['reminder']['unit']
                    )

                    time_to_reject = (auto_reject_time -
                                      current_time).total_seconds()
                    time_to_reminder = (
                        reminder_time - current_time).total_seconds()

                    # Check if reminder should be sent
                    if time_to_reminder <= 0 and not request.get('reminder_sent'):
                        print(f"Sending reminder for request {
                              request['request_id']}")
                        self._send_reminder(request)
                        request['reminder_sent'] = True

                    # Check if request should be auto-rejected
                    if time_to_reject <= 0 and not request.get('auto_rejected'):
                        print(
                            f"Auto-rejecting request {request['request_id']}")
                        self._auto_reject(request)
                        request['auto_rejected'] = True

            except Exception as e:
                print(f"Error in monitoring thread: {str(e)}")
                import traceback
                traceback.print_exc()

            time.sleep(10)  # Check every 10 seconds

    def _send_reminder(self, request: Dict[str, Any]) -> None:
        """Send a reminder for a pending request"""
        try:
            # Check if reminder already sent
            if request.get('reminder_sent'):
                return

            print(f"Sending reminder for request {request['request_id']}")

            # Calculate time remaining until auto-reject
            current_time = datetime.utcnow()
            request_time = datetime.fromisoformat(request['timestamp'])
            auto_reject_time = request_time + self._convert_to_timedelta(
                self.config['timeout']['value'],
                self.config['timeout']['unit']
            )
            time_remaining = (auto_reject_time -
                              current_time).total_seconds() / 60

            # Send reminder notification
            message = (
                f"⚠️ Reminder: Pending membership request for {
                    request['name']} "
                f"({request['role']}) will be auto-rejected in {time_remaining:.1f} minutes. "
                f"Request ID: {request['request_id']}"
            )

            print(f"REMINDER: {message}")

            # Record reminder in blockchain and update request
            self.membership.blockchain.new_transaction(
                sender="0x0000000000000000000000000000000000000000",
                recipient=request['address'],
                data={
                    'type': 'membership_reminder',
                    'request_id': request['request_id'],
                    'message': message,
                    'timestamp': current_time.isoformat(),
                    'time_remaining_minutes': time_remaining
                }
            )

            # Mark reminder as sent in the request object
            request['reminder_sent'] = True
            request['reminder_time'] = current_time.isoformat()

        except Exception as e:
            print(f"Error sending reminder: {str(e)}")
            import traceback
            traceback.print_exc()

    def _auto_reject(self, request: Dict[str, Any]) -> None:
        """Auto-reject a request that has exceeded its time limit"""
        try:
            if not self.config['enabled']:
                return

            # Debug log
            print(f"Executing auto-reject for request {request['request_id']}")

            # Use system address for auto-reject transactions
            SYSTEM_ADDRESS = "0x0000000000000000000000000000000000000000"

            # Force update the request status in membership
            self.membership.update_request_status(
                request_id=request['request_id'],
                status='rejected',
                reason='Auto-rejected due to timeout'
            )

            # Record auto-rejection in blockchain
            self.membership.blockchain.new_transaction(
                sender=SYSTEM_ADDRESS,
                recipient=request['address'],
                data={
                    'type': 'membership_auto_rejected',
                    'request_id': request['request_id'],
                    'reason': 'Request timed out',
                    'timestamp': datetime.utcnow().isoformat(),
                    'auto_reject_enabled': True,
                    'auto_rejected_by': 'system'
                }
            )

            # Debug log
            print(f"Auto-reject completed for request {request['request_id']}")

        except Exception as e:
            print(f"Error in auto-reject: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get the current timing status of a specific request"""
        # Check in pending requests
        request = next(
            (req for req in self.membership.get_pending_requests()
             if req['request_id'] == request_id),
            None
        )

        # If not in pending, check in rejected requests
        if not request:
            request = next(
                (req for req in self.membership.get_rejected_requests()
                 if req['request_id'] == request_id),
                None
            )

        if not request:
            return {
                'error': 'Request not found',
                'request_id': request_id
            }

        current_time = datetime.utcnow()
        request_time = datetime.fromisoformat(request['timestamp'])

        auto_reject_time = request_time + self._convert_to_timedelta(
            self.config['timeout']['value'],
            self.config['timeout']['unit']
        )

        return {
            'request_id': request_id,
            'status': request.get('status', 'pending'),
            'auto_rejected': request.get('auto_rejected', False),
            'time_remaining': (auto_reject_time - current_time).total_seconds(),
            'auto_reject_enabled': self.config['enabled'],
            'timeout_at': auto_reject_time.isoformat()
        }
