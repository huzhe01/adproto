# 解决 Android Studio Gradle Sync 报错指南

## 问题原因
您的 Android Studio 默认使用了 **Java 21/23** (您系统默认是 OpenJDK 23), 但项目配置的 **Gradle 6.5** 最高仅支持 Java 14。

## 解决方案

请在 Android Studio 中将 Gradle JDK 更改为 **Java 1.8**。

### 步骤

1. **打开设置**
   - **Mac**: 点击菜单栏 `Android Studio` -> `Settings...` -> `Build, Execution, Deployment` -> `Build Tools` -> `Gradle`

2. **修改 Gradle JDK**
   - 找到底部的 **"Gradle JDK"** 选项
   - **请选择 `1.8`**
   - 我检测到您的系统已安装 **Eclipse Temurin 8**，它应该出现在列表中。
   - 如果列表中没有，请选择 "Add JDK..." 并指向此路径:
     `/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home`

3. **重新同步**
   - 点击 `Apply` -> `OK`
   - 点击工具栏的 **"Sync Project"** 按钮 (大象图标)

---

### 方法二: 命令行运行

如果您想在终端运行，请先设置 JAVA_HOME 为 Java 8:

```bash
export JAVA_HOME="/Library/Java/JavaVirtualMachines/temurin-8.jdk/Contents/Home"
cd /Users/huzhe/playground/ProtoAd/Simple_Tiktok_App
./gradlew installDebug
```
