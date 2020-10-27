from dsmr_parser import telegram_specifications
from dsmr_parser.parsers import TelegramParser
from dsmr_parser.clients import SerialReader, SERIAL_SETTINGS_V5
from dsmr_parser import obis_references
from retrying import retry
import requests
import jsons
import os
import logging

logging.basicConfig(format='[%(levelname)s] - %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

class SmartMeter():
    def __init__(self, id = None, equipmentIdentifier = None):
        self.id = id
        self.equipmentIdentifier = equipmentIdentifier

    def toJSON(self):
        return jsons.dumps(self)

class LiveMetrics():
    def __init__(self, production = None, productionUnit = None, consumption = None, consumptionUnit = None,
    voltageL1 = None, voltageL1Unit = None, voltageL2 = None, voltageL2Unit = None, voltageL3 = None, voltageL3Unit = None,
    currentL1 = None, currentL1Unit = None, currentL2 = None, currentL2Unit = None, currentL3 = None, currentL3Unit = None,):
        self.production = production
        self.productionUnit = productionUnit
        self.consumption = consumption
        self.consumptionUnit = consumptionUnit
        self.voltageL1 = voltageL1
        self.voltageL1Unit = voltageL1Unit
        self.voltageL2 = voltageL2
        self.voltageL2Unit = voltageL2Unit
        self.voltageL3 = voltageL3
        self.voltageL3Unit = voltageL3Unit
        self.currentL1 = currentL1
        self.currentL1Unit = currentL1Unit
        self.currentL2 = currentL2
        self.currentL2Unit = currentL2Unit
        self.currentL3 = currentL3
        self.currentL3Unit = currentL3Unit

    def toJSON(self):
        return jsons.dumps(self)

class GridMetrics():
    def __init__(self, consumedLow = None, consumedLowUnit = None, consumedNormal = None, consumedNormalUnit = None, deliveredLow = None,
    deliveredLowUnit = None, deliveredNormal = None, deliveredNormalUnit = None, tariff = None, longPowerFailureCount = None, shortPowerFailureCount = None,
    voltageSagL1Count = None, voltageSwellL1Count = None, voltageSagL2Count = None, voltageSwellL2Count = None, voltageSagL3Count = None, voltageSwellL3Count = None):
        self.consumedLow = consumedLow
        self.consumedLowUnit = consumedLowUnit
        self.consumedNormal = consumedNormal
        self.consumedNormalUnit = consumedNormalUnit
        self.deliveredLow = deliveredLow
        self.deliveredLowUnit = deliveredLowUnit
        self.deliveredNormal = deliveredNormal
        self.deliveredNormalUnit = deliveredNormalUnit
        self.tariff = tariff
        self.longPowerFailureCount = longPowerFailureCount
        self.shortPowerFailureCount = shortPowerFailureCount
        self.voltageSagL1Count = voltageSagL1Count
        self.voltageSwellL1Count = voltageSwellL1Count
        self.voltageSagL2Count = voltageSagL2Count
        self.voltageSwell21Count = voltageSwellL2Count
        self.voltageSagL3Count = voltageSagL3Count
        self.voltageSwellL3Count = voltageSwellL3Count

    def toJSON(self):
        return jsons.dumps(self)

class SmartMeterMetrics():
    def __init__(self, messageHeader = None, messageTimestamp = None, smartMeter = None, liveMetrics = None, gridMetrics = None):
        self.messageHeader = messageHeader
        self.messageTimestamp = messageTimestamp
        self.smartMeter = smartMeter
        self.liveMetrics = liveMetrics
        self.gridMetrics = gridMetrics

    def toJSON(self):
        return jsons.dumps(self)

class SmartMetricsReader():
    def __init__(self):
        self.host = os.getenv('FLEXY_BACKEND_HOST', 'http://localhost:8080').strip()
        self.metrics_url = self.host + "/metrics"
        self.meters_url = self.host + "/meters"
        self.logs_url = self.host + "/logs"

        self.serial_reader = SerialReader(
            device='/dev/ttyUSB0',
            serial_settings=SERIAL_SETTINGS_V5,
            telegram_specification=telegram_specifications.V5
        )

        self.metrics = {
            "energy.sensor.electricity.p1_message_header": obis_references.P1_MESSAGE_HEADER,
            "energy.sensor.electricity.p1_message_timestamp": obis_references.P1_MESSAGE_TIMESTAMP,
            "energy.sensor.electricity.equipment_identifier": obis_references.EQUIPMENT_IDENTIFIER,
            "energy.sensor.electricity.live.production": obis_references.CURRENT_ELECTRICITY_DELIVERY,
            "energy.sensor.electricity.live.consumption": obis_references.CURRENT_ELECTRICITY_USAGE,
            "energy.sensor.electricity.live.voltage.l1": obis_references.INSTANTANEOUS_VOLTAGE_L1,
            "energy.sensor.electricity.live.voltage.l2": obis_references.INSTANTANEOUS_VOLTAGE_L2,
            "energy.sensor.electricity.live.voltage.l3": obis_references.INSTANTANEOUS_VOLTAGE_L3,
            "energy.sensor.electricity.live.current.l1": obis_references.INSTANTANEOUS_CURRENT_L1,
            "energy.sensor.electricity.live.current.l2": obis_references.INSTANTANEOUS_CURRENT_L2,
            "energy.sensor.electricity.live.current.l3": obis_references.INSTANTANEOUS_CURRENT_L3,
            "energy.sensor.electricity.grid.consumed.low": obis_references.ELECTRICITY_USED_TARIFF_1,
            "energy.sensor.electricity.grid.consumed.normal": obis_references.ELECTRICITY_USED_TARIFF_2,
            "energy.sensor.electricity.grid.delivered.low": obis_references.ELECTRICITY_DELIVERED_TARIFF_1,
            "energy.sensor.electricity.grid.delivered.normal": obis_references.ELECTRICITY_DELIVERED_TARIFF_2,
            "energy.sensor.electricity.grid.tariff": obis_references.ELECTRICITY_ACTIVE_TARIFF,
            "energy.sensor.electricity.grid.long_power_failure_count": obis_references.LONG_POWER_FAILURE_COUNT,
            "energy.sensor.electricity.grid.short_power_failure_count": obis_references.SHORT_POWER_FAILURE_COUNT,
            "energy.sensor.electricity.grid.voltage_sag_l1_count": obis_references.VOLTAGE_SAG_L1_COUNT,
            "energy.sensor.electricity.grid.voltage_swell_l1_count": obis_references.VOLTAGE_SWELL_L1_COUNT,
            "energy.sensor.electricity.grid.voltage_sag_l2_count": obis_references.VOLTAGE_SAG_L2_COUNT,
            "energy.sensor.electricity.grid.voltage_swell_l2_count": obis_references.VOLTAGE_SWELL_L2_COUNT,
            "energy.sensor.electricity.grid.voltage_sag_l3_count": obis_references.VOLTAGE_SAG_L3_COUNT,
            "energy.sensor.electricity.grid.voltage_swell_l3_count": obis_references.VOLTAGE_SWELL_L3_COUNT,
        }

        self.smart_meter_id = None
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.collected_metrics = []

    def register_meter(self):
        for telegram in self.serial_reader.read():
            self.equipment_identifier = telegram[self.metrics["energy.sensor.electricity.equipment_identifier"]].value
            logging.info('Register meter with equipment_identifier: [%s]', self.equipment_identifier)
            self.smart_meter = SmartMeter(self.smart_meter_id, self.equipment_identifier)
            try:
                self.response = requests.request("POST", self.meters_url, headers=self.headers, data = self.smart_meter.toJSON())
                self.response_json = self.response.json()
                if self.response.status_code == 200:
                    logging.debug('Success! Recieved OK Response: [%s]', self.response_json)
                    self.smart_meter_id = self.response_json['id']
                    logging.debug('Updating smart_meter_id to [%s]', self.smart_meter_id)
                else:
                    logging.error('Failure! Received Response with status [%s] and content [%s]', self.response.status_code, self.response_json)
            except Exception as ex:
                logging.error('Failed to register smart meter [%s]', ex)
                raise ex
            break

    def read_metrics(self):
        logging.info('Collecting metrics for equipment_identifier: [%s]', self.equipment_identifier)
        for telegram in self.serial_reader.read():
            # metrics metadata
            self.p1_message_header = self.valueOrNone(telegram, "energy.sensor.electricity.p1_message_header")
            self.p1_message_timestamp = self.valueOrNone(telegram, "energy.sensor.electricity.p1_message_timestamp")
            self.equipment_identifier = self.valueOrNone(telegram, "energy.sensor.electricity.equipment_identifier")
            self.tariff = self.valueOrNone(telegram, "energy.sensor.electricity.grid.tariff")
            # metrics values
            self.voltage_l1 = self.valueOrNone(telegram, "energy.sensor.electricity.live.voltage.l1")
            self.voltage_l2 = self.valueOrNone(telegram, "energy.sensor.electricity.live.voltage.l2")
            self.voltage_l3 = self.valueOrNone(telegram, "energy.sensor.electricity.live.voltage.l3")
            self.current_l1 = self.valueOrNone(telegram, "energy.sensor.electricity.live.current.l1")
            self.current_l2 = self.valueOrNone(telegram, "energy.sensor.electricity.live.current.l2")
            self.current_l3 = self.valueOrNone(telegram, "energy.sensor.electricity.live.current.l3")
            self.production = self.valueOrNone(telegram, "energy.sensor.electricity.live.production")
            self.consumption = self.valueOrNone(telegram, "energy.sensor.electricity.live.consumption")
            self.consumed_low = self.valueOrNone(telegram, "energy.sensor.electricity.grid.consumed.low")
            self.consumed_normal = self.valueOrNone(telegram, "energy.sensor.electricity.grid.consumed.normal")
            self.delivered_low = self.valueOrNone(telegram, "energy.sensor.electricity.grid.delivered.low")
            self.delivered_normal = self.valueOrNone(telegram, "energy.sensor.electricity.grid.delivered.normal")
            self.long_power_failure_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.long_power_failure_count")
            self.short_power_failure_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.short_power_failure_count")
            self.voltage_sag_l1_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_sag_l1_count")
            self.voltage_swell_l1_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_swell_l1_count")
            self.voltage_sag_l2_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_sag_l2_count")
            self.voltage_swell_l2_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_swell_l2_count")
            self.voltage_sag_l3_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_sag_l3_count")
            self.voltage_swell_l3_count = self.valueOrNone(telegram, "energy.sensor.electricity.grid.voltage_swell_l3_count")
            # metrics units of emasurements
            self.production_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.production")
            self.consumption_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.consumption")
            self.consumed_low_unit = self.unitOrNone(telegram, "energy.sensor.electricity.grid.consumed.low")
            self.consumed_normal_unit = self.unitOrNone(telegram, "energy.sensor.electricity.grid.consumed.normal")
            self.delivered_low_unit = self.unitOrNone(telegram, "energy.sensor.electricity.grid.delivered.low")
            self.delivered_normal_unit = self.unitOrNone(telegram, "energy.sensor.electricity.grid.delivered.normal")
            self.voltage_l1_unit = self.unitOrDefault(telegram, "energy.sensor.electricity.live.voltage.l1", "None")
            self.voltage_l2_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.voltage.l2")
            self.voltage_l3_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.voltage.l3")
            self.current_l1_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.current.l1")
            self.current_l2_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.current.l2")
            self.current_l3_unit = self.unitOrNone(telegram, "energy.sensor.electricity.live.current.l3")

            # instantiate classes
            self.smart_meter = SmartMeter(self.smart_meter_id, self.equipment_identifier)
            self.live_metrics = LiveMetrics(self.production, self.production_unit, self.consumption, self.consumption_unit,
                self.voltage_l1, self.voltage_l1_unit, self.voltage_l2, self.voltage_l2_unit,self.voltage_l3, self.voltage_l3_unit,
                self.current_l1, self.current_l1_unit, self.current_l2, self.current_l2_unit,self.current_l3, self.current_l3_unit)

            self.grid_metrics = GridMetrics(self.consumed_low, self.consumed_low_unit, self.consumed_normal, self.consumed_normal_unit, self.delivered_low, self.delivered_low_unit,
                self.delivered_normal, self.delivered_normal_unit, self.tariff, self.long_power_failure_count, self.short_power_failure_count, self.voltage_sag_l1_count, self.voltage_swell_l1_count,
                self.voltage_sag_l2_count, self.voltage_swell_l2_count, self.voltage_sag_l3_count, self.voltage_swell_l3_count)

            self.smart_meter_metrics = SmartMeterMetrics(self.p1_message_header, self.p1_message_timestamp, self.smart_meter, self.live_metrics, self.grid_metrics)
            logging.debug('Collected Smart Meter Metric: [%s]', self.smart_meter_metrics.toJSON())
            self.collected_metrics.append(self.smart_meter_metrics)

            # post metrics
            self.post_metrics()
            break

    def send_logs(self):
        try:
            url = self.logs_url + '/' + self.equipment_identifier
            with open('/home/pi/flexy-reader-public/dsmr.log', 'rb') as fin:
                files = [('file', fin)]
                self.logs_response = requests.post(url, files = files)
                fin.close()
                if self.logs_response.status_code == 200:
                    logging.info('Recieved OK Response: [%s]', self.logs_response.json()['message'])
                else:
                    logging.error('Failure! Received Response with status [%s] and content [%s]', self.logs_response.status_code, self.logs_response.json())
        except Exception as ex:
            logging.error('Failed to send logs [%s]', ex)

    def valueOrNone(self, telegram, key):
        try:
            return telegram[self.metrics[key]].value
        except:
            return None

    def unitOrNone(self, telegram, key):
        try:
            return telegram[self.metrics[key]].unit
        except:
            return None

    def unitOrDefault(self, telegram, key, defaultValue):
        try:
            return telegram[self.metrics[key]].unit
        except:
            return defaultValue

    def post_metrics(self):
        try:
            self.body = jsons.dumps(self.collected_metrics)
            self.response = requests.request("POST", self.metrics_url, headers=self.headers, data = self.body)
            self.response_json = self.response.json()
            if self.response.status_code == 200:
                logging.info('Success! Recieved Response [%s] when posting metrics', self.response.status_code)
            else:
                logging.info('Failure! Received Response with status [%s] and content [%s]',self.response.status_code, self.response_json)
        except Exception as ex:
            logging.error('Failed to post smart meter metrics [%s]', ex)
            raise ex


def collect_metrics():
    logging.info("Registering smart meter and collecting the metrics.")
    try:
        reader = SmartMetricsReader()
        reader.register_meter()
        # reader.send_logs()
        reader.read_metrics()
    except Exception as ex:
        logging.error('Failed to collect metrics [%s]', ex)
        raise ex

collect_metrics()
