CREATE TABLE Consultants (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL
);

-- Randevular tablosu
CREATE TABLE Appointments (
    ID INT PRIMARY KEY IDENTITY(1,1),
    FullName NVARCHAR(100) NOT NULL,       -- Randevu alan kişinin adı
    Date DATE NOT NULL,                    -- Randevu tarihi
    Time TIME NOT NULL,                    -- Randevu saati
    consultant_id INT NOT NULL,            -- Danışman ID'si (foreign key)
    FOREIGN KEY (consultant_id) REFERENCES Consultants(id)
);
