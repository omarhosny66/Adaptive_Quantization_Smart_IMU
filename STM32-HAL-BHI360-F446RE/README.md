# BHI360 Driver for STM32 Nucleo-F446RE (HAL)

This repository provides a hardware abstraction layer and integration for the Bosch BHI360 Smart IMU on the STM32F446RE microcontroller. This implementation replaces the Bosch COINES dependency with a lightweight platform layer built directly on the STM32Cube HAL, specifically tailored for resource constrained embedded environments.

The BHI360 is a smart sensor hub that requires a firmware upload to its internal RAM/Flash upon startup. Unlike standard IMUs, data is accessed through a structured FIFO event system rather than simple register polling.

---

## Project Structure

The project is organized to separate vendor driver code, hardware abstraction, and application logic.

### 1. Application Layer (`Core/`)
* **`main.c`**: The entry point. Initializes MCU peripherals and coordinates the sensor processing loop.
* **`bosch_imu.c / .h`**: The integration bridge. It contains high-level logic for sensor lifecycle management, including initialization, firmware loading, and virtual sensor configuration.

### 2. Bosch Driver & Platform Layer (`Drivers/BHI360/`)
* **`bhy2.c / .h / _defs.h`**: Official Bosch Sensortec API files for core logic.
* **`bhy2_hif.c`**: Host interface handling.
* **`bhy2_parse.c`**: FIFO data parsing and event extraction.
* **`common.c / .h`**: Contains the platform-specific glue code (I2C and Timing) that replaces the COINES library.
* **`firmware/bhi360_fw.h`**: The binary firmware image required for the BHI360 to function.

### 3. Other Hardware Specific Drivers
The implementation relies on standard STM32F4xx HAL drivers to interface with the MCU hardware:
* **I2C HAL**: Manages the physical bus transactions.
* **UART HAL**: Used for serial data output and debugging.
* **RCC/GPIO HAL**: Configures system clocks and pin assignments for the communication buses.

---

## Hardware Configuration & I2C Interface

### I2C Mode Operation
According to the **Bosch BHI360 Datasheet (Section 4.4.2)**, the device implements an I2C slave interface. 

* **Pull-up Resistors**: External pull-up resistors are required on the SCL and SDA lines (typically 4.7kΩ).
* **Device Address Selection**: The 7-bit address depends on the **HSDO** pin state:
    * **0x29**: HSDO tied HIGH.
    * **0x28**: HSDO tied LOW (used in this project).
* **Clock Speed**: Supports up to 3.4 Mbit/s in high-speed mode. 400 kHz (Fast Mode) is used here for stability.

### STM32CubeMX Setup
| Peripheral | Configuration | Pins |
| :--- | :--- | :--- |
| **I2C1** | Fast Mode (400 kHz) | PB8 (SCL), PB9 (SDA) |
| **USART2** | 115200 Baud, 8N1 | PA2 (TX), PA3 (RX) |

---

## COINES Replacement Implementation

To remove the dependency on Bosch's COINES library, the following platform-specific functions bridge the Bosch API with the STM32 HAL.

```c
/* I2C Read Function for BHY2 API */
int8_t bhy2_i2c_read(uint8_t reg_addr, uint8_t *reg_data, uint32_t length, void *intf_ptr)
{
  (void)intf_ptr;

  if(HAL_I2C_Mem_Read(&hi2c1, 0x28<<1, reg_addr, I2C_MEMADD_SIZE_8BIT, reg_data, (uint16_t)length, 100) == HAL_OK)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

/* I2C Write Function for BHY2 API */
int8_t bhy2_i2c_write(uint8_t reg_addr, const uint8_t *reg_data, uint32_t length, void *intf_ptr)
{
  (void)intf_ptr;

  if(HAL_I2C_Mem_Write(&hi2c1, 0x28<<1, reg_addr, I2C_MEMADD_SIZE_8BIT, (uint8_t *)reg_data, (uint16_t)length, 100) == HAL_OK)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

/* Microsecond Delay for BHY2 API */
void bhy2_delay_us(uint32_t us, void *private_data)
{
  (void)private_data;
  micros_delay((uint64_t)us);
}
```

---

## Software Implementation Details

### 'bosch_imu.c'
This file abstracts the complexity of the Bosch API:
* **`bosch_imu_init()`**: Sets up the `bhy2` device structure with the function pointers for I2C and delays. It handles the mandatory firmware upload from `bhi360_fw.h` and verifies the Chip ID.
* **Sensor Configuration**: Activates specific virtual sensors (e.g., Linear Acceleration) and sets their sample rates.
* **`bosch_imu_process()`**: This is the data handler. It checks the sensor status and pulls data packets from the FIFO to be processed by the parser.

### 'main.c'
The main loop is designed for efficiency:
1. **Peripheral Initialization**: Sets up HAL and system clocks.
2. **Sensor Setup**: Executes `bosch_imu_init()` once.
3. **The Main Loop**: Continuously executes `bosch_imu_process()`. In this implementation, data retrieval is managed via polling the FIFO status, ensuring the buffer is cleared promptly without needing an external interrupt trigger for the core data flow.

---

## Acknowledgments
* The driver logic is based on the [Bosch Sensortec BHY2-Sensor-API](https://github.com/boschsensortec/BHY2-Sensor-API). This port provides a reference for integrating the API into a standard STM32 HAL environment.
* [STM32 HAL BHI360 Reference Implementation](https://github.com/Dmivaka/STM32-HAL-BHI360)

