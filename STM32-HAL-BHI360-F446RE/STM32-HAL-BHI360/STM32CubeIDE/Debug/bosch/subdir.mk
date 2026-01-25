################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (10.3-2021.10)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../bosch/bhi3.c \
../bosch/bhi3_multi_tap.c \
../bosch/bhy2_bsec.c \
../bosch/bhy2_head_tracker.c \
../bosch/bhy2_klio.c \
../bosch/bhy2_swim.c 

OBJS += \
./bosch/bhi3.o \
./bosch/bhi3_multi_tap.o \
./bosch/bhy2_bsec.o \
./bosch/bhy2_head_tracker.o \
./bosch/bhy2_klio.o \
./bosch/bhy2_swim.o 

C_DEPS += \
./bosch/bhi3.d \
./bosch/bhi3_multi_tap.d \
./bosch/bhy2_bsec.d \
./bosch/bhy2_head_tracker.d \
./bosch/bhy2_klio.d \
./bosch/bhy2_swim.d 


# Each subdirectory must supply rules for building sources it contributes
bosch/%.o bosch/%.su: ../bosch/%.c bosch/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F446xx -c -I../../Core/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../Drivers/CMSIS/Include -I"C:/BHI360/STM32-HAL-BHI360-F446RE/STM32-HAL-BHI360/STM32CubeIDE/bosch" -I"C:/BHI360/STM32-HAL-BHI360-F446RE/STM32-HAL-BHI360/STM32CubeIDE/bosch/common" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-bosch

clean-bosch:
	-$(RM) ./bosch/bhi3.d ./bosch/bhi3.o ./bosch/bhi3.su ./bosch/bhi3_multi_tap.d ./bosch/bhi3_multi_tap.o ./bosch/bhi3_multi_tap.su ./bosch/bhy2_bsec.d ./bosch/bhy2_bsec.o ./bosch/bhy2_bsec.su ./bosch/bhy2_head_tracker.d ./bosch/bhy2_head_tracker.o ./bosch/bhy2_head_tracker.su ./bosch/bhy2_klio.d ./bosch/bhy2_klio.o ./bosch/bhy2_klio.su ./bosch/bhy2_swim.d ./bosch/bhy2_swim.o ./bosch/bhy2_swim.su

.PHONY: clean-bosch

