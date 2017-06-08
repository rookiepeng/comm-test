/*
//    mainwindow.cpp
//
//    Copyright (C) 2017  Zach (Zhengyu) Peng, https://zpeng.me
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "myudp.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    initUI();

    targetAddr.setAddress(ui->targetIPEdit->text());
    targetPort=ui->targetPortEdit->text().toInt();

    connect(ui->pushButton,SIGNAL(clicked()),this,SLOT(sendMessage()));
    connect(ui->sendEdit,SIGNAL(returnPressed()),this,SLOT(sendMessage()));
    connect(ui->targetIPEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));
    connect(ui->targetPortEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));
    connect(ui->listenPortEdit,SIGNAL(textChanged(QString)),this,SLOT(enableUpdateButton()));
    connect(ui->updateButton,SIGNAL(clicked()),this,SLOT(updateConfig()));

    myudp=new MyUDP;
    connect(myudp,SIGNAL(newMessage(QString,QString)),this,SLOT(appendMessage(QString,QString)));
    connect(myudp,SIGNAL(bindSuccess(bool)),this,SLOT(udpBinded(bool)));
    myudp->bindPort(ui->listenPortEdit->text().toInt());
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::initUI()
{
    QString rule = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])";
    ui->targetIPEdit->setValidator(new QRegExpValidator(QRegExp("^" + rule + "\\." + rule + "\\." + rule + "\\." + rule + "$"), this));
    ui->targetPortEdit->setValidator(new QIntValidator(0, 65535, this));
    ui->listenPortEdit->setValidator(new QIntValidator(0, 65535, this));

    ui->messageBrowser->setFocusPolicy(Qt::NoFocus);

    ui->sendEdit->setFocusPolicy(Qt::StrongFocus);
    ui->sendEdit->setFocus();

    tableFormat.setBorder(0);

    loadSettings();
}

void MainWindow::appendMessage(const QString &from, const QString &message)
{
    if (from.isEmpty() || message.isEmpty())
        return;

    QTextCursor cursor(ui->messageBrowser->textCursor());
    cursor.movePosition(QTextCursor::End);

    QTextTable *table = cursor.insertTable(1, 2, tableFormat);
    table->cellAt(0, 0).firstCursorPosition().insertText('<' + from + "> ");
    table->cellAt(0, 1).firstCursorPosition().insertText(message);
    QScrollBar *bar = ui->messageBrowser->verticalScrollBar();
    bar->setValue(bar->maximum());
}

void MainWindow::sendMessage()
{
    QString text = ui->sendEdit->text();
    if (text.isEmpty())
        return;

    if (text.startsWith(QChar('/'))) {
        QColor color = ui->messageBrowser->textColor();
        ui->messageBrowser->setTextColor(Qt::red);
        ui->messageBrowser->append(tr("! Unknown command: %1")
                                   .arg(text.left(text.indexOf(' '))));
        ui->messageBrowser->setTextColor(color);
    } else {
        myudp->sendMessage(targetAddr,targetPort,text);
        appendMessage("client", text);
        //myudp->sendMessage(text);
    }

    ui->sendEdit->clear();
}

void MainWindow::udpBinded(bool isBinded)
{
    ui->updateButton->setDisabled(isBinded);
}

void MainWindow::enableUpdateButton()
{
    ui->updateButton->setDisabled(false);
}

void MainWindow::updateConfig()
{
    disconnect(this,SLOT(appendMessage(QString,QString)));
    disconnect(this,SLOT(udpBinded(bool)));
    targetAddr.setAddress(ui->targetIPEdit->text());
    targetPort=ui->targetPortEdit->text().toInt();
    myudp->unBind();
    delete myudp;
    myudp=new MyUDP;
    connect(myudp,SIGNAL(newMessage(QString,QString)),this,SLOT(appendMessage(QString,QString)));
    connect(myudp,SIGNAL(bindSuccess(bool)),this,SLOT(udpBinded(bool)));
    myudp->bindPort(ui->listenPortEdit->text().toInt());
    saveSettings();
}

void MainWindow::loadSettings()
{
    settingsFileDir = QApplication::applicationDirPath() + "/config.ini";
    QSettings settings(settingsFileDir, QSettings::IniFormat);
    ui->targetIPEdit->setText(settings.value("targetIP", "127.0.0.1").toString());
    ui->targetPortEdit->setText(settings.value("targetPort", 1234).toString());
    ui->listenPortEdit->setText(settings.value("listenPort", 1234).toString());
}

void MainWindow::saveSettings()
{
    QSettings settings(settingsFileDir, QSettings::IniFormat);
    settings.setValue("targetIP", ui->targetIPEdit->text());
    settings.setValue("targetPort", ui->targetPortEdit->text());
    settings.setValue("listenPort", ui->listenPortEdit->text());
    settings.sync();
}
