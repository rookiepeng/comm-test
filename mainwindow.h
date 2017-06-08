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
    void loadSettings();

    void saveSettings();

    Ui::MainWindow *ui;
    QTextTableFormat tableFormat;
    MyUDP *myudp;
    QHostAddress senderAddr;
    quint16 senderPort;
     QString m_sSettingsFile;
};

#endif // MAINWINDOW_H
