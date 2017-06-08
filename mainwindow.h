#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTextTable>
#include <QScrollBar>
#include <QSettings>

#include "myudp.h"

#define ROLE 1 // 0 server, 1 client

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public slots:
    void appendMessage(const QString &from, const QString &message);

private slots:
    void sendMessage();
    void udpBinded(bool isBinded);
    void enableUpdateButton();
    void updateConfig();

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private:
    Ui::MainWindow *ui;
    void initUI();
    void loadSettings();
    void saveSettings();

    QTextTableFormat tableFormat;
    MyUDP *myudp;
    QHostAddress targetAddr;
    quint16 targetPort;
    QString settingsFileDir;
};

#endif // MAINWINDOW_H
